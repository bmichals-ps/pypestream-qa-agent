# -*- coding: utf-8 -*-
r'''
    ______  ______  _____________________  _________    __  ___
   / __ \ \/ / __ \/ ____/ ___/_  __/ __ \/ ____/   |  /  |/  /
  / /_/ /\  / /_/ / __/  \__ \ / / / /_/ / __/ / /| | / /|_/ /
 / ____/ / / ____/ /___ ___/ // / / _, _/ /___/ ___ |/ /  / /
/_/     /_/_/   /_____//____//_/ /_/ |_/_____/_/  |_/_/  /_/
action node script

'''

import argparse
import os
import time

from util import (
    OCRMatch,
    click_text,
    find_text,
    get_screen_change_score,
    open_chromium_with_url,
    safe_sleep,
    save_screenshot,
    type_text,
)


class PypestreamVisionRPAAgent:
    def __init__(self, preview_url: str, work_dir: str):
        self.preview_url = preview_url
        self.work_dir = work_dir
        self.logs_dir = os.path.join(work_dir, "logs")
        self.screens_dir = os.path.join(work_dir, "screenshots")
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.screens_dir, exist_ok=True)
        self.log_path = os.path.join(self.logs_dir, "run.log")

    def log(self, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def wait_for_text(self, targets, timeout_s: int = 30) -> OCRMatch | None:
        end = time.time() + timeout_s
        while time.time() < end:
            match = find_text(targets)
            if match:
                return match
            safe_sleep(1.0)
        return None

    def attempt_click(self, targets, description: str, timeout_s: int = 20) -> bool:
        self.log(f"Looking for {description}.")
        match = self.wait_for_text(targets, timeout_s=timeout_s)
        if not match:
            self.log(f"Unable to find {description}.")
            save_screenshot(self.screens_dir, f"missing_{description}")
            return False
        click_text(match)
        self.log(f"Clicked {description}.")
        safe_sleep(1.5)
        return True

    def fill_field(self, label_targets, value: str, description: str) -> bool:
        match = find_text(label_targets)
        if not match:
            self.log(f"Field label not found: {description}.")
            return False
        click_text(match, x_offset=120)
        safe_sleep(0.3)
        type_text(value)
        self.log(f"Entered {description}.")
        return True

    def proceed_next(self) -> bool:
        return self.attempt_click(
            ["Next", "Continue", "Proceed"],
            description="next/proceed button",
            timeout_s=10,
        )

    def handle_structured_intake(self) -> None:
        self.log("Starting structured intake flow.")
        field_map = [
            (["Policy Number", "Policy #", "Policy"], "PLCY-12345", "policy number"),
            (["ZIP", "Zip Code", "Postal"], "10001", "zip code"),
            (["Date of Incident", "Incident Date", "Date"], "01/02/2025", "date"),
            (["First Name"], "Test", "first name"),
            (["Last Name"], "User", "last name"),
            (["Phone", "Phone Number"], "5551234567", "phone number"),
            (["Email"], "test.user@example.com", "email"),
        ]
        for labels, value, desc in field_map:
            self.fill_field(labels, value, desc)
            safe_sleep(0.5)

        self.attempt_click(["Yes", "Safe to live", "Safe"], "safe-to-live yes")
        self.attempt_click(["No", "Injuries"], "injuries no")

        for _ in range(6):
            if not self.proceed_next():
                safe_sleep(1.0)
            else:
                safe_sleep(2.0)

    def handle_review_screen(self) -> None:
        self.log("Looking for review screen proceed.")
        self.attempt_click(["Proceed to Next Section", "Proceed"], "review proceed button")

    def handle_chat_mode(self) -> None:
        self.log("Entering chat mode loop.")
        idle_cycles = 0
        while idle_cycles < 15:
            if self.handle_address_request():
                idle_cycles = 0
                continue
            button_match = find_text(["Yes", "No", "Continue", "Next", "Proceed"])
            if button_match:
                click_text(button_match)
                self.log("Clicked chat quick-reply button.")
                idle_cycles = 0
                safe_sleep(1.5)
                continue
            input_match = find_text(
                ["Type", "Enter", "Write", "Message", "Say something"]
            )
            if input_match:
                click_text(input_match, y_offset=25)
                safe_sleep(0.2)
                type_text("Test response.")
                self.log("Sent chat text response.")
                idle_cycles = 0
                safe_sleep(1.5)
                continue
            idle_cycles += 1
            safe_sleep(1.0)

        self.log("Chat loop ended without further prompts.")

    def handle_address_request(self) -> bool:
        address_prompt = find_text(["Address", "Policy Address", "Search address"])
        if not address_prompt:
            return False
        self.log("Address prompt detected.")
        click_text(address_prompt, y_offset=30)
        safe_sleep(0.4)
        type_text("123 Main St, New York, NY")
        safe_sleep(1.0)
        type_text("\n")
        safe_sleep(1.5)
        self.attempt_click(["Proceed", "Next"], "address proceed button", timeout_s=5)
        return True

    def execute(self) -> None:
        self.log("Launching Chromium.")
        open_chromium_with_url(self.preview_url)
        safe_sleep(6.0)

        last_score = None
        self.log("Attempting to click Engage with us.")
        if not self.attempt_click(
            ["Engage with us", "Engage"], "Engage with us button", timeout_s=20
        ):
            self.log("Engage button not found. Aborting.")
            return

        safe_sleep(4.0)
        self.handle_structured_intake()
        self.handle_review_screen()
        safe_sleep(3.0)

        for _ in range(3):
            score = get_screen_change_score()
            if last_score is not None and score < 0.02:
                self.log("Screen not changing; capturing diagnostics.")
                save_screenshot(self.screens_dir, "no_progress")
            last_score = score
            safe_sleep(2.0)

        self.handle_chat_mode()
        self.log("Run completed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vision RPA for Pypestream preview URLs")
    parser.add_argument("preview_url", help="Preview URL for the Pypestream solution")
    parser.add_argument(
        "--work-dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Directory for logs and screenshots",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent = PypestreamVisionRPAAgent(args.preview_url, args.work_dir)
    agent.execute()


if __name__ == "__main__":
    main()
