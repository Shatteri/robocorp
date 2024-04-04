from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
import shutil
from pathlib import Path

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Downloads the orders CSV file, reads it as a table, and returns the result.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    close_annoying_modal()
    download_csv_file("https://robotsparebinindustries.com/orders.csv")
    orders = get_orders("orders.csv")
    print(orders)
    loop_orders(orders)
    archive_receipts()

def open_robot_order_website():
    """Navigates to the given URL"""
    page = browser.page()
    browser.goto("https://robotsparebinindustries.com/")
    page.click("text=Order your robot!")

def download_csv_file(url):
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url=url, overwrite=True)

def get_orders(csv_file_path):
    """Reads the CSV file as a table and returns it."""
    tables = Tables()
    table = tables.read_table_from_csv(csv_file_path, header=True)
    return table

def loop_orders(orders):
    """Loops through orders"""
    for order in orders:
        fill_the_form(order)

def close_annoying_modal():
    """Closes the annoying modal"""
    page = browser.page()
    page.click("text=OK")

def fill_the_form(order):
    """Fills the robot ordering form"""
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    choice_value = str(order["Body"])
    page.click(f"input[type='radio'][value='{choice_value}']")
    page.fill("input.form-control", str(order["Legs"]))
    page.fill("#address", str(order["Address"]))
    page.click("text=Preview")
    retry = True
    while retry == True:
        page.click("id=order")
        if page.locator("id=order-completion").is_visible():
            retry = False

    order_number = str(order["Order number"])
    store_receipt_as_pdf(order_number)
    page.click("id=order-another")
    close_annoying_modal()

def store_receipt_as_pdf(order_number):
    """Stores the order receipt as a PDF file"""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    file_name = f"order_{order_number}_receipt.pdf"
    pdf.html_to_pdf(order_receipt_html, "output/receipts/"+file_name)
    screenshot_robot(order_number)

def screenshot_robot(order_number):
    """Takes a screenshot of the robot"""
    page = browser.page()
    screenshot_path = f"output/receipts/order_{order_number}_screenshot.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    embed_screenshot_to_receipt(screenshot_path, f"output/receipts/order_{order_number}_receipt.pdf")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """"Embeds the screenshot to the corresponding receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=pdf_file
    )

def archive_receipts():
    """Archives the receipts into a zip file"""
    directory_path = Path("output/receipts")
    archive_name = "archived_receipts"
    archive_path = Path("output") / archive_name
    shutil.make_archive(archive_path, 'zip', directory_path)