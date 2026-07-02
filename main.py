import argparse

from job_tracker.tracker import add_application, summarize_applications

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Application Tracker")
    parser.add_argument("url", nargs="?", default="", help="The application link")
    parser.add_argument("properties", nargs="*", help="Additional properties in the format 'PropName:PropValue'")
    parser.add_argument("--list", action="store_true", help="Print a summary of tracked applications instead of adding a new one")
    parser.add_argument(
        "--stale-after",
        type=int,
        default=14,
        metavar="DAYS",
        help="With --list, flag 'Applied' applications with no status update after this many days (default: 14)",
    )
    args = parser.parse_args()

    if args.list:
        summarize_applications(stale_after_days=args.stale_after)
    elif args.url:
        add_application(args.url, args.properties)
    else:
        parser.error("the following arguments are required: url (or pass --list)")
