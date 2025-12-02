function calculateNotificationTime(dateString)
{
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    const intervals = {
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1
    }

    const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' });

    for (const [unit, interval] of Object.entries(intervals)) {

        if (seconds >= interval) {
            if (unit === "day") {
                // For notifications older than a day, show the date
                return date.toLocaleString();
            }
            else {
                const value = Math.floor(seconds / interval);
                return rtf.format(-value, unit);
            }
        }

        if (unit === "second" && seconds < 10) {
            return "Just Now";
        }
    }

}