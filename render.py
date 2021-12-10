from datetime import datetime as dt
import sys

raw = """
.row.project
  .col-md-2.col-3
    h3.mb-0 %%%DAY%%%
    h5.month.mb-0 %%%MONTH%%%
    p 15:00-16:00
  .col-md-7.col-9
    p.author #[span.me %%%AUTHOR%%%]
    h5.title.mb-1
      | %%%TITLE%%%
    .btn-group.btn-group-sm(role="group",aria-label="Commands").mt-1
      a(href="%%%CALENDAR%%%").btn.btn-primary
        | #[i.bi.bi-calendar-event-fill] Add to Calendar
      a(data-bs-toggle="collapse",href="#%%%TALK_ID%%%",role="button",aria-expanded="false",aria-controls="collapseExample").btn.btn-primary%%%DISABLED%%%
        | #[i.bi.bi-file-earmark-text-fill] Abstract
  .col-md-7
    p.abstract#%%%TALK_ID%%%.collapse.mt-2
        | %%%ABSTRACT%%%
      """

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

# Read file name
try:
    filename = sys.argv[1]
except IndexError:
    print('Usage: render.py <csv_filename>')
    sys.exit(1)

# Parse CSV file into a dictionary
with open(filename, 'r') as f:
    lines = f.readlines()
    header = lines[0].strip().split(',')
    data = {}
    for line in lines[1:]:
        row = line.strip().split(',')
        data[row[0]] = dict(zip(header[1:], row[1:]))

# Iterate over the dictionary
for date, talk in data.items():
    # Skip if no name
    if not talk['Name']:
        continue

    # Parse date
    date = dt.strptime(date, '%d/%m/%Y')

    # Get month name
    month = date.strftime('%B')

    # Get cardinal day without leading zero
    day = str(int(date.strftime('%d')))

    # Add suffix to day
    day += suffix(int(day))

    # Build the output
    output = raw.replace('%%%DAY%%%', day)
    output = output.replace('%%%MONTH%%%', month)
    output = output.replace('%%%AUTHOR%%%', talk['Name'])
    output = output.replace('%%%TITLE%%%', talk['Title'])

    # Eventually add abstract
    if talk['Abstract']:
        output = output.replace('%%%ABSTRACT%%%', talk['Abstract'])
        output = output.replace('%%%DISABLED%%%', '')
    else:
        output = output.replace('%%%ABSTRACT%%%', 'No abstract available')
        output = output.replace('%%%DISABLED%%%', '.disabled')

    # Eventually add calendar link
    if 'Calendar' in talk and talk['Calendar']:
        output = output.replace('%%%CALENDAR%%%', talk['Calendar'])
    else:
        output = output.replace('%%%CALENDAR%%%', '#')

    # Generate talk ID from the author using md5
    import hashlib
    talk_id = hashlib.md5(talk['Name'].encode('utf-8')).hexdigest()

    # Add talk ID to output
    output = output.replace('%%%TALK_ID%%%', talk_id)

    # Print output
    print(output)
