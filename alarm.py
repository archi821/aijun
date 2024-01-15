import schedule
import time

def job():
    print("該起床了...")
schedule.every().day.at("9:30", "Asia/Taipei").do(job)

def job1():
    print("該睡覺了...")
schedule.every().day.at("0:00", "Asia/Taipei").do(job1)

def job_with_argument(name):
    print(f"我是 {name}")

schedule.every(10).seconds.do(job_with_argument, name="あい")

while True:
    schedule.run_pending()
    time.sleep(1)

