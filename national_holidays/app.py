import csv
import datetime
import io
import os
import shutil
import urllib.request


def fetch_national_holidays(destination: str) -> None:
    # 内閣府「国民の祝日」 https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html
    with urllib.request.urlopen(
        "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
    ) as f:
        body = f.read()

    with open(os.path.join(destination, "national_holidays.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(("date", "name"))

        reader = csv.DictReader(io.StringIO(body.decode("shift-jis")))
        writer.writerows(
            (
                datetime.datetime.strptime(
                    row["国民の祝日・休日月日"], "%Y/%m/%d"
                ).strftime("%Y-%m-%d"),
                row["国民の祝日・休日名称"],
            )
            for row in reader
        )


def copy_schema_file(destination: str):
    shutil.copyfile(
        os.path.join(
            os.path.dirname(__file__), "national_holidays_schema.json"
        ),
        os.path.join(destination, "national_holidays_schema.json"),
    )


def main():
    destination = os.environ["DESTINATION"]
    os.makedirs(destination, exist_ok=True)
    fetch_national_holidays(destination)
    copy_schema_file(destination)


if __name__ == "__main__":
    main()
