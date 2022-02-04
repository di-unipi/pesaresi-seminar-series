from csv import DictReader
from datetime import datetime as dt
import hashlib

raw = """
.row.project
  .col-md-2.col-3
    h3.mb-0 %%%DAY%%%
    h5.month.mb-0 %%%MONTH%%%
    p 15:00-16:00
  .col-md-7.col-9
    p.author #[span.me %%%AUTHOR%%%]
    h4.title.mb-1
      | %%%TITLE%%%
    .btn-group.btn-group-sm(role="group",aria-label="Commands").mt-1
      a(href="%%%CALENDAR%%%",target="_blank").btn.btn-primary
        | #[i.bi.bi-calendar-event-fill] Add to Calendar
      button.btn.btn-primary(type="button",data-bs-toggle="collapse",data-bs-target="#%%%TALK_ID%%%",aria-expanded="false",aria-controls="%%%TALK_ID%%%"%%%DISABLED%%%)
        | #[i.bi.bi-file-earmark-text-fill] Abstract%%%SLIDES%%%
  .col-md-7
    p.abstract#%%%TALK_ID%%%.collapse.mt-2
        | %%%ABSTRACT%%%"""

raw_upcoming = """
.row.next
  .col-md-7.col-8
    p.author #[span.me %%%AUTHOR%%%]
    h2.title.mb-0.mt-1
      | %%%TITLE%%%
  .col-md-2.col-4
    h1.day %%%DAY%%%
    h4.month.mb-0 %%%MONTH%%%
    p 15:00-16:00
  .col-md-7.col-12.mt-sm-3.mt-lg-1
      p
        | %%%ABSTRACT%%%
  .col-md-4.d-grid.gap-2.d-md-block
    a(href="%%%CALENDAR%%%",target="_blank").btn.btn-primary.mb-md-3.w-100
      | #[i.bi.bi-calendar-event-fill] Add to Calendar
    a(href="%%%MEET%%%").btn.btn-primary.mb-md-3.w-100
      | #[i.bi.bi-camera-reels-fill] Live Streaming
      """

slides_raw = """
      a(href="%%%SLIDES%%%",target="_blank").btn.btn-primary
        | #[i.bi.bi-easel3-fill] Slides"""

# Button for in presence location
# a(href="https://goo.gl/maps/FL4qcbB3MnMXrYS28",target="_blank").btn.btn-primary.w-100
#   | #[i.bi.bi-geo-alt-fill] Sala Seminari Est


def render_talk(talk, upcoming=False, slides=False):
    if upcoming:
        template = raw_upcoming
    else:
        template = raw

    # Parse date
    date = dt.strptime(talk['Date'], '%d/%m/%Y')

    # Get month name
    month = date.strftime('%B')

    # Get cardinal day without leading zero
    day = str(int(date.strftime('%d')))

    # Add suffix to day
    day += suffix(int(day))

    # Build the output
    output = template.replace('%%%DAY%%%', day)
    output = output.replace('%%%MONTH%%%', month)
    output = output.replace('%%%AUTHOR%%%', talk['Name'])
    output = output.replace('%%%TITLE%%%', talk['Title'])

    # Eventually add abstract
    if talk['Abstract']:
        output = output.replace('%%%ABSTRACT%%%', talk['Abstract'])
        output = output.replace('%%%DISABLED%%%', '')
    else:
        output = output.replace('%%%ABSTRACT%%%', 'No abstract available')
        output = output.replace('%%%DISABLED%%%',
                                ',aria-disabled="true",disabled')

    # Eventually add calendar link
    if 'Calendar' in talk and talk['Calendar']:
        output = output.replace('%%%CALENDAR%%%', talk['Calendar'])
    else:
        output = output.replace('%%%CALENDAR%%%', '#')

    # Eventually add meet link
    if 'Meet' in talk and talk['Meet']:
        output = output.replace('%%%MEET%%%', talk['Meet'])
    else:
        output = output.replace('%%%MEET%%%', '#')

    # Eventually add slides link
    if slides:
        output = output.replace('%%%SLIDES%%%',
                                slides_raw.replace('%%%SLIDES%%%',
                                                   f'slides/{talk["Title"]}'
                                                   '.pdf'))
    else:
        output = output.replace('%%%SLIDES%%%', '')

    # Generate talk ID from the author using md5
    talk_id = hashlib.md5(talk['Name'].encode('utf-8')).hexdigest()

    # DOM Selectors can't start with a number
    talk_id = 'talk-' + talk_id

    # Add talk ID to output
    output = output.replace('%%%TALK_ID%%%', talk_id)

    return output


def suffix(d):
    return 'th' if 11 <= d <= 13 \
            else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


if __name__ == '__main__':
    import argparse

    # Parse arguments
    parser = argparse.ArgumentParser(description='Render talks')
    parser.add_argument('-u', '--upcoming', action='store_true',
                        help='Render upcoming talks')
    parser.add_argument('-d', '--date', type=str,
                        help='Render page for a specific date '
                             '(format: DD/MM/YYYY)')
    parser.add_argument('csv_filename', type=str,
                        help='CSV file containing talks')
    args = parser.parse_args()

    # Parse CSV file into a dictionary
    with open(args.csv_filename, 'r') as fp:
        csv_reader = DictReader(fp)
        talks = list(csv_reader)

    # Get current datetime
    if not args.date:
        now = dt.now()
    else:
        now = dt.strptime(args.date, '%d/%m/%Y')

    # Filter talks
    talks = [talk for talk in talks if talk['Name']]
    future = [talk for talk in talks if dt.strptime(talk['Date'],
                                                    '%d/%m/%Y') > now]
    past = [talk for talk in talks if dt.strptime(talk['Date'],
                                                  '%d/%m/%Y') <= now]

    # Assign upcoming
    if future and args.upcoming:
        upcoming = future[0]
        future = future[1:]
    else:
        upcoming = None

    # Render upcoming
    with open('src/upcoming.pug', 'w') as f:
        if upcoming:
            f.write('.row.mt-4.mb-2\n')
            f.write('  h2 #[span.emoji 🚀] Upcoming\n')
            f.write(render_talk(upcoming, True))
        else:
            f.write('')

    # Render past talks
    with open('src/past.pug', 'w') as f:
        if past:
            f.write('.row.mt-4.mb-4\n')
            f.write('  h2 #[span.emoji ⌛️] Past Talks\n')
            for talk in past:
                f.write(render_talk(talk, slides=True))
        else:
            f.write('')

    # Render future talks
    with open('src/next.pug', 'w') as f:
        if future:
            f.write('.row.mt-4.mb-4\n')
            f.write('  h2 #[span.emoji 🔮] Next Talks\n')
            for talk in future:
                f.write(render_talk(talk))
        else:
            f.write('')
