from django.shortcuts import render
import requests
from django.db import connection
#import matplotlib.pyplot as plt
import pprint
from datetime import datetime
from django.utils import timezone
import random
import io
import base64

def Item():
    destination_airport=[]
    origin_airport=[]
    airline=[]
    
    #distinct ORIGIN_AIRPORT
    cmd="select distinct ORIGIN_AIRPORT from dataset"
    cursor=connection.cursor()
    t=cursor.execute(cmd);
    ori=cursor.fetchall()
    for i in ori:
        origin_airport.append(i[0])
        
    #distinct DESTINATION_AIPORT
    cmd="select distinct DESTINATION_AIRPORT from dataset"
    cursor=connection.cursor()
    t=cursor.execute(cmd);
    des=cursor.fetchall()
    for i in des:
        destination_airport.append(i[0])
        
    #distinct airline
    cmd="SELECT DISTINCT AIRLINE FROM `dataset` WHERE AIRLINE is not null"
    cursor=connection.cursor()
    t=cursor.execute(cmd);
    air=cursor.fetchall()
    for i in air:
        airline.append(i[0])
        
    show={
        'origin_airport':origin_airport,
        'destination_airport':destination_airport,
        'airline':airline
    }
    return show





def visualization(from_date,to_date,airline,source,destination):
    if from_date != '' or to_date != '' or airline != '' or source != '' or destination != '':
        filter=" where"
        if from_date != '':
            filter=filter+" Date_reportted >= '"+from_date+"' and"
        if to_date !='':
            filter=filter+" Date_reportted <= '"+to_date+"' and"
        if airline != '':
            filter=filter+" AIRLINE = '"+airline+"' and"
        if source !='':
            filter=filter+" ORIGIN_AIRPORT = '"+source+"' and"
        if destination !='':
            filter=filter+" DESTINATION_AIRPORT = '"+destination+"' and"
        filter=filter.rsplit(' ',1)[0]
    else:
        filter=""
        print('No filters')
    #first, *middle, last=filter.split()
    print('.............................')
    print(filter)
    return filter


def getCardData(filter):
    #total airline and flights
    print(len(filter)==0)
    cards_cmd="select count(distinct AIRLINE), count(*) from dataset"+filter
    print("CARD CMD--------------------------------------------")
    print(cards_cmd)
    
    cursor=connection.cursor()
    t=cursor.execute(cards_cmd);
    airline_flight=cursor.fetchall()
    airline=airline_flight[0][0]
    flights=airline_flight[0][1]
    print(airline_flight[0])
    
    #delay flights
    if len(filter)==0:
        delay_cmd="select count(*) from dataset where total_delay=0"
    else:
        delay_cmd="select count(*) from dataset"+filter+"and total_delay=0"
    cursor=connection.cursor()
    t=cursor.execute(delay_cmd);
    delay=cursor.fetchall()
    on_time=delay[0][0]
    delay=flights-on_time

    #cancelled flights
    if len(filter)==0:
        cancel_cmd="select count(*) from dataset where CANCELLED=1"
    else:
        cancel_cmd="select count(*) from dataset"+filter+"and CANCELLED=1"

    cursor=connection.cursor()
    t=cursor.execute(cancel_cmd);
    cancel=cursor.fetchall()
    cancel=cancel[0][0]

    cards_data={
        'total_airline':airline,
        'total_flights':flights,
        'on_time_flights':on_time,
        'delay_flights':delay,
        'cancelled_flights':cancel
    }
    return cards_data

def getPieChartData(filter,cards_data):
    pie_cmd="select * from dataset "+filter+"limit 2"
    print("PICMD--------------------------------------------")
    print(pie_cmd)
    cursor=connection.cursor()
    t=cursor.execute(pie_cmd);
    pie_chart_data=list(cursor.fetchall())
    total_flights=cards_data['total_flights']
    if cards_data['total_flights']!=0:
    #print(cards_data['total_flights'])
        on_time=(cards_data['on_time_flights']/cards_data['total_flights'])*100
        delay=(cards_data['delay_flights']/cards_data['total_flights'])*100
    else:
        on_time=0
        delay=0

    pie_chart_data={
        'name':['On Time','Delay'],
        'series':[round(on_time,2),round(delay),],
        'labels':[str(round(on_time,2))+"%",str(round(delay))+"%",]
    }
    print(pie_chart_data)
    return pie_chart_data


# def delayChart(filter,cards_data):
#     #delay_cmd="SELECT Date_reportted, AIRLINE, AVG(total_delay) FROM `dataset` group by AIRLINE, Date_reportted;"+str(filter)+""
#     delay_cmd="SELECT AVG(total_delay), CONCAT(year(Date_reportted),'-', month(Date_reportted)) as Date_reportted, AIRLINE FROM `dataset` GROUP by AIRLINE,CONCAT(year(Date_reportted),'-', month(Date_reportted)) ORDER by Date_reportted,AIRLINE"+str(filter)+""
#     cursor=connection.cursor()
#     t=cursor.execute(delay_cmd);
#     delay_chart_data=list(cursor.fetchall())
#     print(cards_data['total_airline'])
#     delay = [data[0] for data in delay_chart_data]
#     airline = [data[1] for data in delay_chart_data]
#     # plt.fill_between(delay, airline, alpha=0.5)
#     # plt.plot(delay, airline)

#     delay_chart_data={
#         'labels':['delay','airline'],
#         'series':[delay,airline]
#     }
#     print(delay_chart_data)
#     return delay_chart_data


def delayChart(filter):
    
    if len(filter)==0:
        delay_cmd="select round(AVG(total_delay),2), concat(month(Date_reportted),' ',year (Date_reportted)) as Date_reportted, AIRLINE from dataset where AIRLINE is NOT NULL group by AIRLINE, concat(month(Date_reportted),' ',year(Date_reportted)) order by AIRLINE"
    else:
        delay_cmd="select round(AVG(total_delay),2), concat(month(Date_reportted),' ', year(Date_reportted)) as Date_reportted, AIRLINE from dataset "+filter+" and AIRLINE is NOT NULL group by AIRLINE, concat(month(Date_reportted),' ',year(Date_reportted)) order by AIRLINE"
      
    cursor=connection.cursor()
    t=cursor.execute(delay_cmd)
    delay_chart_data_cur=cursor.fetchall()
    airline=[]
    temp_labels=[]
    temp={}
    count=0
    #print("ssssssssssssssssssssssssssssssssssss")
    for a, b, c in delay_chart_data_cur:
        if not c in airline:
            temp_series=[]
            airline.append(c)
            count=count+1
        if not b in temp_labels:
            date=datetime.strptime(b, '%m %Y')
            temp_labels.append(date)
        temp_series.append(a)
        temp_labels.sort()
        temp[count]={'airline':c,'series':temp_series,'labels':temp_labels}
    #print("....................temp...................")    
    #pprint.pprint(temp)
    airline=[]
    labels=[]
    series=[]
    
    for i in temp.values():
        airline.append(i['airline'])
        series.append(i['series'])
        for l in i['labels']:
            new_l=l.strftime('%b-%Y')
            if new_l not in labels:
                labels.append(new_l)
    
    # labels.sort()
    #color=colorGenerator(len(airline))
    color=['#1DC7EA','#FB404B','#FFA534','#9368E9','#87CB16','#1F77D0','#5e5e5e','#dd4b39',
            '#35465c','#e52d27','#55acee','#cc2127','#1769ff','#78829a']
    
    airline_color={}
    print(airline)
    for k in range(len(airline)):
        print(k)
        airline_color[airline[k]]=color[k]
    print(airline_color)
    delay_chart_data={
        # 'airlines':airline,
        'labels':labels,
        'series':series,
        'airline_color':airline_color
        # 'colors':color
    }
    print('delayc-----------------------------------------------')
    pprint.pprint(delay_chart_data)
    
    return delay_chart_data 



def barChart(filter):
    if len(filter)==0:
        bar_cmd="select round(AVG(DEPARTURE_DELAY),2) as DEPARTURE_DELAY, round(AVG(ARRIVAL_DELAY),2) as ARRIVAL_DELAY, concat(month(Date_reportted),' ',year(Date_reportted)) as Date_reportted from dataset where AIRLINE is NOT NULL group by concat(month(Date_reportted),' ',year(Date_reportted))"
    else:
        bar_cmd="select round(AVG(DEPARTURE_DELAY),2) as DEPARTURE_DELAY, round(AVG(ARRIVAL_DELAY),2) as ARRIVAL_DELAY, concat(month(Date_reportted),' ',year(Date_reportted)) as Date_reportted from dataset "+filter+" and AIRLINE is NOT NULL group by concat(month(Date_reportted),' ',year(Date_reportted))"
        
    cursor=connection.cursor()
    t=cursor.execute(bar_cmd);
    bar_chart_data_cur=cursor.fetchall()
    # print(bar_chart_data_cur)
    departure_delay=[]
    arrival_delay=[]
    date=[]
    
    
    for a,b,c in bar_chart_data_cur:
        departure_delay.append(a)
        arrival_delay.append(b)
        temp_date=datetime.strptime(c, '%m %Y')
        temp_date=temp_date.strftime('%b-%Y')
        date.append(temp_date)
    delay_reasons=['Departure Delay','Arrival Delay']
    color=['#FF5733','#33FF3C']
    delayReason_color={}
    for k in range(len(delay_reasons)):
        delayReason_color[delay_reasons[k]]=color[k]
    print(delayReason_color)
    bar_chart_data={
        'labels':date,
        'series':[departure_delay, arrival_delay],
        'delayReason_color':delayReason_color
    }
    return bar_chart_data
        
    
    
#     Delay_reason=[item[0] for item in bar_chart_data]
#     airline = [item[1] for item in bar_chart_data]

#     bar_chart_data={
#         'labels':['delay','airline'],
#         'series':[Delay_reason,airline]
#     }

def dashboard(request):
    from_date=request.GET.get('fromdate','')
    to_date=request.GET.get('todate','')
    airline=request.GET.get('airline','')
    source=request.GET.get('origin_airport','')
    destination=request.GET.get('destination_airport','')
    
    show=Item()

    filter=visualization(from_date,to_date,airline,source,destination)
    print(filter)
    cmd="select * from dataset "+filter

    #for cards.........
    cards_data=''
    cards_data=getCardData(filter)
 
    #for pie chart.........
    pie_chart_data=getPieChartData(filter,cards_data)
    
    #for delay chart...........
    delay_chart_data=delayChart(filter)
    
    #for bar chart..............
    bar_chart_data=barChart(filter)
    
    
    data={
        'cards_data':cards_data,
        'pie_chart_data':pie_chart_data,
        'delay_chart_data':delay_chart_data,
        'bar_chart_data':bar_chart_data,
        'filter':filter,
        'show':show,
    }
    print(show)
    
    
    # print(pie_chart_data)
    return render(request,'dashboard.html',data)


    
    

 #bar chart
    # bar_chart_data=barChart(filter,cards_data)
    # data={
    #     'cards_data':cards_data,
    #     'bar_chart_data':bar_chart_data,
    #     'filter':filter,
    # }
