import asyncio
import os
import shutil
from datetime import date, datetime, timedelta

import holidays
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from sh import lpr
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Select, Static, ProgressBar
from textual.worker import get_current_worker

#  Define basic elements to construct our calendar.
STATUS_CLOSED = "4_Asset_ClosedToday.png"
#  Study Room assets
SR_WEEKDAY_HOURS = "SR_0_Asset_WeekdayHours.png"
SR_FRIDAY_HOURS = "SR_1_Asset_FridayHours.png"
SR_SATURDAY_HOURS = "SR_2_Asset_SaturdayHours.png"
SR_SUNDAY_HOURS = "SR_3_Asset_SundayHours.png"
#  Program Room assets
PR_WEEKDAY_HOURS = "PR_0_Asset_WeekdayHours.png"
PR_FRIDAY_HOURS = "PR_1_Asset_FridayHours.png"
PR_SATURDAY_HOURS = "PR_2_Asset_SaturdayHours.png"
PR_SUNDAY_HOURS = "PR_3_Asset_SundayHours.png"


#  Define our fonts and sizes.
DATE_STRING_FONT = ImageFont.truetype("SF-Pro-Text-Black.ttf", 80)

#  Define a dictionary of holidays and special dates, some of which we are closed on or imprint artwork for.

#  Holiday name or date; artwork location; whether closed or not.
#  Reset dates each year as soon as the new calendar is available.

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


def year_to_print_for(answer_):
    if datetime.today().month >= 11 and answer_ <= 2:
        return datetime.today().year + 1
    return datetime.today().year


def printing_end_date(answer_, year_to_print_for_, answer_as_number_):
    if answer_ == "December":
        return date(year_to_print_for_ + 1, 1, 1)
    return date(year_to_print_for_, answer_as_number_ + 1, 1)


def overlays(calendar_sheet_, calendar_sheet_filename_, art_to_use_, building_closure_):
    """Imprint closure and/or holiday artwork."""
    # Convert calendar_sheet to RGBA mode to properly handle alpha channels
    if calendar_sheet_.mode != "RGBA":
        calendar_sheet_ = calendar_sheet_.convert("RGBA")

    # Create a composite of artwork and closure status first if both are present
    if art_to_use_ and building_closure_:
        artwork_image = Image.open(art_to_use_).convert("RGBA")
        closure_image = Image.open(STATUS_CLOSED).convert("RGBA")

        # Composite artwork and closure together first
        # Create a new transparent image with the same size as the calendar sheet
        combined_overlay = Image.new("RGBA", calendar_sheet_.size, (0, 0, 0, 0))
        combined_overlay = Image.alpha_composite(combined_overlay, artwork_image)
        combined_overlay = Image.alpha_composite(combined_overlay, closure_image)

        # Now composite the combined overlay onto the calendar sheet
        calendar_sheet_ = Image.alpha_composite(calendar_sheet_, combined_overlay)
    else:
        # Handle cases where only one overlay is present
        if art_to_use_:
            artwork_image = Image.open(art_to_use_).convert("RGBA")
            calendar_sheet_ = Image.alpha_composite(calendar_sheet_, artwork_image)

        if building_closure_:
            closure_image = Image.open(STATUS_CLOSED).convert("RGBA")
            calendar_sheet_ = Image.alpha_composite(calendar_sheet_, closure_image)

    calendar_sheet_.save(calendar_sheet_filename_, format="png")


def daterange_to_print(first_date_, last_date_):
    for n in range(int((last_date_ - first_date_).days)):
        yield first_date_ + timedelta(n)


def standard_week(single_date_, study_room_mode):
    """Create a mutable calendar sheet based on the mode and current day of the week."""
    if study_room_mode:
        match single_date_.weekday():
            case 6:
                calendar_sheet_ = Image.open(SR_SUNDAY_HOURS).convert("RGB").copy()
            case 5:
                calendar_sheet_ = Image.open(SR_SATURDAY_HOURS).convert("RGB").copy()
            case 4:
                calendar_sheet_ = Image.open(SR_FRIDAY_HOURS).convert("RGB").copy()
            case _:
                calendar_sheet_ = Image.open(SR_WEEKDAY_HOURS).convert("RGB").copy()
    else:
        match single_date_.weekday():
            case 6:
                calendar_sheet_ = Image.open(PR_SUNDAY_HOURS).convert("RGB").copy()
            case 5:
                calendar_sheet_ = Image.open(PR_SATURDAY_HOURS).convert("RGB").copy()
            case 4:
                calendar_sheet_ = Image.open(PR_FRIDAY_HOURS).convert("RGB").copy()
            case _:
                calendar_sheet_ = Image.open(PR_WEEKDAY_HOURS).convert("RGB").copy()
    return calendar_sheet_


def draw_dates(calendarsheet_, single_date_):
    """Draw dates on each day of the calendar."""
    draw_dates_ = ImageDraw.Draw(calendarsheet_)
    draw_dates_.text(
        (3274, 114),
        single_date_.strftime("%A — %b, %d, %Y"),
        (0, 0, 0),
        anchor="rs",
        font=DATE_STRING_FONT,
    )


def check_image_exists(image_path):
    if not os.path.exists(image_path):
        return False
    return True


def sendprintjob(calendar_month_name_):
    if not shutil.which("lpr"):
        return False
    else:
        try:
            lpr("-o", "media=Letter",
                "-o", "sides=one-sided",
                "-o", "print-quality=5",
                "-#", "1",
                f"months/{calendar_month_name_}.pdf")
            return True
        except Exception as e:
            print(f"Error sending print job: {str(e)}")
            return False


class RoomsCalendarApp(App):
    """A Textual app to generate room calendars."""

    theme = "catppuccin-latte"

    CSS = """
    Screen {
        background: #f9dd51;
        color: black;
    }

    #main-container {
        layout: vertical;
        padding: 1 2;
        height: 100%;
        background: #f9dd51;
        color: black;
    }

    #title {
        text-align: center;
        text-style: bold;
        width: 100%;
        margin-bottom: 1;
        color: black;
    }

    #options-container {
        layout: horizontal;
        height: auto;
        margin-bottom: 1;
    }

    .option-group {
        width: 50%;
        height: auto;
        padding: 1;
        border: solid black;
        margin-right: 1;
        background: #f9dd51;
        color: black;
    }

    .option-label {
        text-style: bold;
        margin-bottom: 1;
        color: black;
    }

    #status-container {
        height: auto;
        margin-top: 1;
        margin-bottom: 1;
    }

    #status-message {
        height: auto;
        padding: 1;
        border: solid black;
        background: #f9dd51;
        color: black;
    }

    #progress-container {
        height: auto;
        margin-top: 1;
    }

    #generate-button {
        margin-top: 1;
        width: 100%;
        background: #f9dd51;
        color: black;
        border: solid black;
    }

    #print-button {
        margin-top: 1;
        width: 100%;
        background: #f9dd51;
        color: black;
        border: solid black;
    }

    Button:hover {
        background: #e9cd41;
    }

    Select {
        background: #f9dd51;
        color: black;
        border: solid black;
    }

    Select > .option {
        background: #f9dd51;
        color: black;
    }

    Select > .option--highlighted {
        background: #e9cd41;
    }

    Footer {
        background: #f9dd51;
        color: black;
    }

    ProgressBar {
        color: black;
    }

    #progress-text {
        text-align: center;
        margin-top: 1;
        color: black;
    }

    .success {
        color: #aaffaa;
    }

    .error {
        color: #ffaaaa;
    }
    """

    TITLE = "Rooms Calendar Generator"
    BINDINGS = [("q", "quit", "Quit")]

    # Reactive variables
    status_message = reactive("Ready to generate calendar")
    progress_value = reactive(0.0)
    calendar_month_name = reactive("")
    can_print = reactive(False)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # Get next month as default
        next_month = (datetime.today().replace(day=28) + timedelta(days=4)).strftime("%B")

        # Create month options
        month_options = [
            (month, month) for month in [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
        ]

        # Create room type options
        room_options = [
            ("Study Room", True),
            ("Program Room", False)
        ]

        with Container(id="main-container"):
            yield Static("Rooms Calendar Generator", id="title")

            with Horizontal(id="options-container"):
                with Vertical(classes="option-group"):
                    yield Static("Select Month:", classes="option-label")
                    yield Select(month_options, value=next_month, id="month-select")

                with Vertical(classes="option-group"):
                    yield Static("Select Room Type:", classes="option-label")
                    yield Select(room_options, value=True, id="room-type-select")

            yield Button("Generate & Print Calendar", id="generate-button")

            with Container(id="status-container"):
                yield Static(self.status_message, id="status-message")

            with Container(id="progress-container"):
                yield ProgressBar(total=100, id="progress-bar")
                yield Static("0%", id="progress-text")

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one("#progress-bar").update(progress=0)
        self.query_one("#progress-text").update("0%")

    @on(Button.Pressed, "#generate-button")
    def generate_calendar(self) -> None:
        """Handle the generate button press."""
        self.status_message = "Checking assets..."
        self.query_one("#status-message").update(self.status_message)
        self.query_one("#generate-button").disabled = True
        self.can_print = False

        # Start the generation process in a worker
        self.generate_calendar_worker()

    @work(exclusive=True)
    async def generate_calendar_worker(self) -> None:
        """Generate the calendar in a background worker."""
        worker = get_current_worker()

        # Get selected values
        month_select = self.query_one("#month-select")
        room_type_select = self.query_one("#room-type-select")

        month_name = month_select.value
        study_room_mode = room_type_select.value
        mode_label = "Study Room" if study_room_mode else "Program Room"

        # Update status
        self.status_message = f"Running version {var_version} in {mode_label} mode."
        self.query_one("#status-message").update(self.status_message)

        # Check for required font
        if not os.path.exists("SF-Pro-Text-Black.ttf"):
            self.status_message = "Error: SF-Pro-Text-Black.ttf not found. Please ensure the font is in the working directory."
            self.query_one("#status-message").update(self.status_message)
            self.query_one("#status-message").add_class("error")
            self.query_one("#generate-button").disabled = False
            return

        # Check for required assets
        assets_to_check = [
            STATUS_CLOSED,
            SR_WEEKDAY_HOURS, SR_FRIDAY_HOURS, SR_SATURDAY_HOURS, SR_SUNDAY_HOURS,
            PR_WEEKDAY_HOURS, PR_FRIDAY_HOURS, PR_SATURDAY_HOURS, PR_SUNDAY_HOURS
        ]

        for asset in assets_to_check:
            if not check_image_exists(asset):
                self.status_message = f"Error: Missing required image: {asset}"
                self.query_one("#status-message").update(self.status_message)
                self.query_one("#status-message").add_class("error")
                self.query_one("#generate-button").disabled = False
                return

        try:
            # Process dates
            var_answer_as_number = datetime.strptime(month_name, "%B").month
            var_year_to_print_for = year_to_print_for(var_answer_as_number)
            var_printing_start_date = date(var_year_to_print_for, var_answer_as_number, 1)
            var_printing_end_date = printing_end_date(
                month_name, var_year_to_print_for, var_answer_as_number
            )

            # Update status
            self.status_message = f"Generating calendar for {month_name} {var_year_to_print_for}..."
            self.query_one("#status-message").update(self.status_message)

            # Initialize PDF merger
            merger = PdfMerger()
            var_michigan_holidays = holidays.US(subdiv="MI", years=var_year_to_print_for)

            # Create directories
            os.makedirs("pages", exist_ok=True)
            os.makedirs("months", exist_ok=True)

            # Calculate total days for progress tracking
            total_days = (var_printing_end_date - var_printing_start_date).days

            # Generate calendar pages
            for i, var_single_date in enumerate(daterange_to_print(
                    var_printing_start_date, var_printing_end_date
            )):
                # Update progress
                progress_percent = (i / total_days) * 100
                self.query_one("#progress-bar").update(progress=progress_percent)
                self.query_one("#progress-text").update(f"{progress_percent:.1f}%")

                # Add a small delay to make progress bar movement visible
                await asyncio.sleep(0.05)

                # Check if worker should stop
                if worker.is_cancelled:
                    self.status_message = "Calendar generation cancelled."
                    self.query_one("#status-message").update(self.status_message)
                    self.query_one("#generate-button").disabled = False
                    return

                var_calendar_sheet_filename = var_single_date.strftime(
                    "pages/Calendar %A %b %d %Y.pdf"
                )

                # Figure out which image should be the basis for our calendar page
                var_calendar_sheet = standard_week(var_single_date, study_room_mode)

                # Draw correct dates
                draw_dates(var_calendar_sheet, var_single_date)

                # Check for holidays
                holiday_name = var_michigan_holidays.get(var_single_date)
                formatted_date = var_single_date.strftime("%Y-%m-%d")

                sth = mpm_holidays.get(holiday_name) or mpm_holidays.get(formatted_date)
                if sth:
                    overlays(var_calendar_sheet, var_calendar_sheet_filename, *sth)

                # Save the calendar page
                var_calendar_sheet.save(var_calendar_sheet_filename, format="pdf")

                # Add to merger
                merger.append(var_calendar_sheet_filename)

            # Complete the progress bar
            self.query_one("#progress-bar").update(progress=100)
            self.query_one("#progress-text").update("100.0%")

            # Save the merged PDF
            self.calendar_month_name = f"{mode_label}_{month_name}_{var_year_to_print_for}"
            merger.write(f"months/{self.calendar_month_name}.pdf")
            merger.close()

            # Clean up temporary files
            for file in os.scandir("pages"):
                os.remove(file.path)

            # Update status
            self.status_message = f"Successfully created {mode_label} calendar for {month_name} {var_year_to_print_for}. Now sending to printer..."
            self.query_one("#status-message").update(self.status_message)
            self.query_one("#status-message").remove_class("error")

            # Set can_print flag and call print_calendar_worker
            self.can_print = True
            self.print_calendar_worker()

        except Exception as e:
            self.status_message = f"Error: {str(e)}"
            self.query_one("#status-message").update(self.status_message)
            self.query_one("#status-message").add_class("error")

        # Re-enable generate button
        self.query_one("#generate-button").disabled = False

    @work(thread=True)
    def print_calendar_worker(self) -> None:
        """Print the calendar in a background worker."""
        if not self.calendar_month_name:
            return

        # Check if the PDF file exists
        pdf_path = f"months/{self.calendar_month_name}.pdf"
        if not os.path.exists(pdf_path):
            self.status_message = f"Error: PDF file not found at {pdf_path}"
            self.query_one("#status-message").update(self.status_message)
            self.query_one("#status-message").add_class("error")
            return

        # Try to send the print job
        success = sendprintjob(self.calendar_month_name)

        if success:
            self.status_message = "Calendar sent to Office Ricoh C4500. Please find your prints there."
            self.query_one("#status-message").update(self.status_message)
            self.query_one("#status-message").add_class("success")
        else:
            self.status_message = "Error: Could not send to printer. Check if lpr command is available and printer is connected."
            self.query_one("#status-message").update(self.status_message)
            self.query_one("#status-message").add_class("error")


if __name__ == "__main__":
    app = RoomsCalendarApp()
    app.run()
