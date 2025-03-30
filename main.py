import os
import shutil
from datetime import date, datetime, timedelta

import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from rich.console import Console
from rich.progress import Progress
from sh import lpr
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Header, Footer, Input, Label, Static, RadioSet, RadioButton

# Define basic elements to construct our calendar.
STATUS_CLOSED = "4_Asset_ClosedToday.png"
# Study Room assets
SR_WEEKDAY_HOURS = "SR_0_Asset_WeekdayHours.png"
SR_FRIDAY_HOURS = "SR_1_Asset_FridayHours.png"
SR_SATURDAY_HOURS = "SR_2_Asset_SaturdayHours.png"
SR_SUNDAY_HOURS = "SR_3_Asset_SundayHours.png"
# Program Room assets
PR_WEEKDAY_HOURS = "PR_0_Asset_WeekdayHours.png"
PR_FRIDAY_HOURS = "PR_1_Asset_FridayHours.png"
PR_SATURDAY_HOURS = "PR_2_Asset_SaturdayHours.png"
PR_SUNDAY_HOURS = "PR_3_Asset_SundayHours.png"

# Define our font.
FONT_PATH = "SF-Pro-Text-Black.ttf"
DATE_STRING_FONT = ImageFont.truetype(FONT_PATH, 80)

# Holidays and special dates dictionary.
mpm_holidays = {
    "New Year's Day": (None, True),
    "New Year's Day (Observed)": (None, True),
    "Martin Luther King Jr. Day": (None, True),
    "2025-02-14": (None, False),
    "2025-02-17": (None, True),
    "Washington's Birthday": (None, False),
    "2025-04-18": (None, True),
    "2025-04-19": (None, True),
    "2025-05-24": (None, True),
    "Memorial Day": (None, True),
    "2025-06-07": (None, True),
    "2025-06-19": (None, True),
    "Independence Day": (None, True),
    "2025-07-05": (None, True),
    "2025-08-30": (None, True),
    "Labor Day": (None, True),
    "2025-10-13": (None, True),
    "Veterans Day": (None, True),
    "Veterans Day (Observed)": (None, True),
    "Thanksgiving": (None, True),
    "Day After Thanksgiving": (None, True),
    "2025-11-29": (None, True),
    "Christmas Eve": (None, True),
    "Christmas Eve (Observed)": (None, True),
    "Christmas Day": (None, True),
    "2025-12-26": (None, True),
    "2025-12-27": (None, True),
    "New Year's Eve": (None, True),
}

var_version = "2025"


def year_to_print_for(month_number: int) -> int:
    if datetime.today().month >= 11 and month_number <= 2:
        return datetime.today().year + 1
    return datetime.today().year


def printing_end_date(month_name: str, year_to_print_for_: int, month_number: int) -> date:
    if month_name == "December":
        return date(year_to_print_for_ + 1, 1, 1)
    return date(year_to_print_for_, month_number + 1, 1)


def overlays(calendar_sheet, calendar_sheet_filename, art_to_use, building_closure):
    """Imprint closure and/or holiday artwork."""
    if art_to_use:
        overlay_img = Image.open(art_to_use).convert("RGBA")
        calendar_sheet.paste(overlay_img, (0, 0), mask=overlay_img)
    if building_closure:
        closure_img = Image.open(STATUS_CLOSED).convert("RGBA")
        calendar_sheet.paste(closure_img, (0, 0), mask=closure_img)
    calendar_sheet.save(calendar_sheet_filename, format="PDF", resolution=100.0)
    ensure_pdf_eof(calendar_sheet_filename)


def daterange_to_print(first_date, last_date):
    total_days = (last_date - first_date).days
    for n in range(total_days):
        yield first_date + timedelta(n)


def standard_week(single_date, study_room_mode: bool):
    """Create a mutable calendar sheet based on the mode and day of the week."""
    weekday = single_date.weekday()
    if study_room_mode:
        if weekday == 6:
            img_path = SR_SUNDAY_HOURS
        elif weekday == 5:
            img_path = SR_SATURDAY_HOURS
        elif weekday == 4:
            img_path = SR_FRIDAY_HOURS
        else:
            img_path = SR_WEEKDAY_HOURS
    else:
        if weekday == 6:
            img_path = PR_SUNDAY_HOURS
        elif weekday == 5:
            img_path = PR_SATURDAY_HOURS
        elif weekday == 4:
            img_path = PR_FRIDAY_HOURS
        else:
            img_path = PR_WEEKDAY_HOURS

    return Image.open(img_path).convert("RGB").copy()


def draw_dates(calendarsheet, single_date):
    """Draw dates on the calendar page."""
    draw_instance = ImageDraw.Draw(calendarsheet)
    draw_instance.text(
        (3274, 114),
        single_date.strftime("%A — %b, %d, %Y"),
        (0, 0, 0),
        anchor="rs",
        font=DATE_STRING_FONT,
    )


def check_image_exists(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Missing required image: {image_path}")


def ensure_pdf_eof(pdf_path):
    """Ensure that the PDF file at pdf_path ends with the proper EOF marker."""
    with open(pdf_path, "rb") as f:
        content = f.read()
    if not content.strip().endswith(b"%%EOF"):
        with open(pdf_path, "ab") as f:
            f.write(b"\n%%EOF")


def send_print_job(calendar_month_name):
    if not shutil.which("lpr"):
        Console().print("[bold red]Warning: lpr command not found. Print job not sent.[/bold red]")
    else:
        lpr(
            [
                "-o media=A4",
                "-o sides=one-sided",
                "-o print-quality=5",
                "-# 1",
                f"months/{calendar_month_name}.pdf",
            ]
        )


def generate_calendar(month_name: str, study_room_mode: bool, console: Console) -> str:
    """
    Generates the calendar PDF for the given month and room mode.
    Returns the path to the generated PDF.
    """
    try:
        month_name = month_name.capitalize()
        month_number = datetime.strptime(month_name, "%B").month
    except ValueError:
        console.print("[bold red]Invalid month name. Please enter a valid month.[/bold red]")
        return ""

    year_to_print = year_to_print_for(month_number)
    printing_start_date = date(year_to_print, month_number, 1)
    printing_end_date_ = printing_end_date(month_name, year_to_print, month_number)

    merger = PdfMerger()
    michigan_holidays = holidays.US(subdiv="MI", years=year_to_print)

    # Check required assets.
    for asset in [
        STATUS_CLOSED,
        SR_WEEKDAY_HOURS,
        SR_FRIDAY_HOURS,
        SR_SATURDAY_HOURS,
        SR_SUNDAY_HOURS,
        PR_WEEKDAY_HOURS,
        PR_FRIDAY_HOURS,
        PR_SATURDAY_HOURS,
        PR_SUNDAY_HOURS,
        FONT_PATH,
    ]:
        check_image_exists(asset)

    os.makedirs("pages", exist_ok=True)

    with Progress(transient=True) as progress:
        task = progress.add_task("Creating calendar...", total=(printing_end_date_ - printing_start_date).days)
        for single_date in daterange_to_print(printing_start_date, printing_end_date_):
            calendar_sheet_filename = single_date.strftime("pages/Calendar %A %b %d %Y.pdf")
            calendar_sheet = standard_week(single_date, study_room_mode)
            draw_dates(calendar_sheet, single_date)

            holiday_name = michigan_holidays.get(single_date)
            formatted_date = single_date.strftime("%Y-%m-%d")
            holiday_art = mpm_holidays.get(holiday_name) or mpm_holidays.get(formatted_date)
            if holiday_art:
                overlays(calendar_sheet, calendar_sheet_filename, *holiday_art)
            else:
                # Save without overlays if no holiday art.
                calendar_sheet.save(calendar_sheet_filename, format="PDF", resolution=100.0)
                ensure_pdf_eof(calendar_sheet_filename)
            merger.append(calendar_sheet_filename)
            progress.advance(task)
    calendar_month_name = f"{'StudyRoom' if study_room_mode else 'ProgramRoom'}_{month_name}_{year_to_print}"
    os.makedirs("months", exist_ok=True)
    output_pdf = f"months/{calendar_month_name}.pdf"
    merger.write(output_pdf)
    merger.close()

    # Clean up individual pages.
    for file in os.scandir("pages"):
        os.remove(file.path)

    send_print_job(calendar_month_name)
    return output_pdf


class CalendarApp(App):
    CSS_PATH = "styles.css"  # Optionally define CSS styles for layout

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Container():
            yield Label("Calendar Generator", id="title")
            with Horizontal():
                yield Label("Month:")
                yield Input(placeholder="e.g., June", id="month_input")
            with Horizontal():
                yield Label("Room Mode:")
                with RadioSet(id="room_mode"):
                    yield RadioButton("Study Room", value="study", id="study")
                    yield RadioButton("Program Room", value="program", id="program")
            yield Button("Generate Calendar", id="generate")
            yield Static("", id="status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate":
            month_input = self.query_one("#month_input", Input).value.strip()
            # Note the corrected argument order here:
            room_mode_widget = self.query_one("#room_mode", RadioSet)
            room_mode = room_mode_widget.pressed_button.value == "study" if room_mode_widget.pressed_button else True

            status_widget = self.query_one("#status", Static)
            status_widget.update("Generating calendar... Please wait.")
            self.refresh()

            # Generate calendar and capture output PDF path.
            console = Console(record=True)
            try:
                pdf_path = generate_calendar(month_input, room_mode, console)
                if pdf_path:
                    status_widget.update(
                        f"[bold green]Successfully created calendar: {pdf_path}[/bold green]\nCheck your printer output as well.")
                else:
                    status_widget.update("[bold red]Calendar generation failed.[/bold red]")
            except Exception as e:
                status_widget.update(f"[bold red]Error: {e}[/bold red]")
                console.print_exception()

if __name__ == "__main__":
    CalendarApp().run()
