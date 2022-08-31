import boto3
from datetime import datetime, timedelta, date
import plotly.graph_objs as go
from plotly.subplots import make_subplots
# AWS Region for the cloudwatch Metrics.
AWS_REGION = "us-east-1"
session = boto3.Session(profile_name='Prod-Profile')
client = session.client('cloudwatch', region_name=AWS_REGION)

startDate=datetime(2022, 8, 19, 0, 0, 0)
endDate=datetime(2022, 8, 25, 23, 59, 59)
total_days = (endDate - startDate).days + 1
dataset = []
for dayNumber in range(total_days):
    current_date = (startDate + timedelta(days=dayNumber)).date()
    dt_start = datetime.combine(current_date, datetime.min.time())
    dt_end = datetime.combine(current_date, datetime.max.time())
    print(dt_start)
    print(dt_end)
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'identifier',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'dz/prod/DP/lag',
                        'MetricName': 'lag_out_ms',
                        'Dimensions': [
                            {
                                'Name': 'service',
                                'Value': 'con-tvinsight'
                            }
                        ]
                    },
                    'Period': 60,
                    'Stat': 'p95',
                }
            },
        ],
        #    StartTime=datetime(2022, 8, 15, 0, 0, 0),
        #    EndTime=datetime(2022, 8, 15, 23, 59, 59)
        StartTime=dt_start,
        EndTime=dt_end
    )
    #(len(response['MetricDataResults'][0]['Values']))
    dataset.append(response['MetricDataResults'][0]['Values'])
print(response)
uptime_percentage = []
for i in dataset:
    count = 0
    #print(len(i))
    for x in i:
        #print(x)
        if x <= 5000:
            count = count + 1
    uptime_percentage.append(count)

output = {}
graph = []
for x,y in zip(uptime_percentage,range(total_days)):
    current_date = (startDate + timedelta(days=y)).date()
    percentage = ((x/len(dataset[1]))*100)
    output[current_date] = percentage
    temp_graph_value = go.Indicator(mode="gauge+number", value=percentage, gauge = {'axis': {'range': [98, 100]}}, domain={'row' : 1, 'column' : 1}, title={'text': str(current_date)})
    graph.append(temp_graph_value)
print(len(graph))

if len(graph) % 2 == 0:
    cols_value = len(graph)/2
else:
    cols_value = int(len(graph)/2) +1
specs_value = [[{'type': 'indicator'}],[{'type': 'indicator'}]]
specs_value[0].extend(specs_value[0]*int((cols_value-1)))
specs_value[1].extend(specs_value[1]*int((cols_value-1)))

fig = make_subplots(
    rows=2,
    cols= int(cols_value),
    specs = specs_value,
)

for i,j in zip(graph,range(0,len(graph))):
    if j < int(len(graph)/2):
        fig.append_trace(i, row=1, col=j+1)
    else:
        fig.append_trace(i, row=2, col=j - int(len(graph)/2) + 1)

fig.show()
