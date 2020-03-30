from django.shortcuts import render
from .forms import ResetForm
from accounts.views import Login, Logout, signup
from accounts.models import Profile
from django.db.models import Q
import numpy as np
import random

import datetime
from dateutil.relativedelta import relativedelta
import calendar as cal
import itertools

def yoshico(request):
    data = Profile.objects.filter(Q(days__isnull = False) | Q(days_late__isnull = False))
    f = ResetForm(request.POST or None)
    if request.method == 'POST' and f.is_valid():
        if f.cleaned_data['reset'] == "reset":
            data = Profile.objects.filter(Q(days__isnull = False) | Q(days_late__isnull = False))
            for d in data:
                d.days = None
                d.days_late = None
                d.save()
            
    return render(request, 'shiftapp/yoshico.html', {'data': data, 'f': f, })
    
def num_to_list (num):
    return [num]

#誰がいつ入れるかのリストを返す。

def make_baseshift(data):
   
    ls = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    
    for d in data:
        name = d.name
        daysls = days_to_list(d.days)
        daysls_late = days_to_list(d.days_late)
        for day in daysls:
            ls[day].append(name)
        for day in daysls_late:
            ls[day].append('*'+ name)
        
    return ls
    
#days 1.2.3.4.5 → [1,2,3,4,5]
def days_to_list(days):
    d1 = 0
    d10 = 0
    ls = []
    
    if days == None:
        return []
    
    for day in days:
        if day.isdecimal() and day.isalnum():
            if int(d1) == 0:
                d1 = int(day)
            else:
                d10 = d1
                d1 = int(day)
            
        elif day == '.' or day == ',':
            if d10 * 10 + d1 != 0 and not (d10 * 10 + d1 in ls):
                ls.append(d10 * 10 + d1)
            
            d1 = 0
            d10 = 0
        
    if d10 * 10 + d1 != 0 and not (d10 * 10 + d1 in ls):
        ls.append(d10 * 10 + d1)
        
    return ls

#["a","b","c","d"]→ [["a","b"],["a","c"],["a","d"], , , ,]
def member_to_pair(member, dic):
    n = len(member)
    ls = []
    LS = []
    Ls = []
    lS = []
    if n == 0:
        return []
    elif n == 1 or n == 2:
        return [member]
    else:
        for i, m1 in zip(range(n-1), member[0:-1]):
            for m2 in member[i+1:n]:
                if (dic[m1] == '1' or dic[m2] == '1') and (m1[0] != '*' and m2[0] != '*'):
                    LS.append([m1, m2])
                elif m1[0] != '*' and m2[0] != '*':
                    Ls.append([m1, m2])
                elif m1[0] != '*' or m2[0] != '*':
                    lS.append([m1, m2])
                else:
                    ls.append([m1, m2])
                    
    if LS != []:
        return LS
    elif Ls != []:
        return Ls
    elif lS != []:
        return lS
    else:
        return ls
    
    
def eval(shift, member_list):
    late_count = 0
    nls = []
    nls2 = []
    ls = list(itertools.chain.from_iterable(shift))
    for member in member_list:
        n = ls.count(member)
        n_late = ls.count('*'+ member)
        late_count += n_late
        nls.append(n + n_late)
        nls2.append(member + ':'+ str(n + n_late))
    return - np.var(nls) - late_count, nls2
        
        
def choiceshift(basels, member_list):
    maxeval = -1000000
    for i in range(50000):
        shift = []
        for k in basels:
            if k == []:
                shift.append(k)
            else:
                shift.append(random.choice(k))
        ev, nls = eval(shift, member_list)
        if maxeval <= ev:
            maxeval = ev
            best_shift = shift
            bnls = nls

    return best_shift, bnls
    
            
            
def makeshift(request):
    date = datetime.date.today()
    next_month = date.replace(day=1) + relativedelta(months=1)
    cal.setfirstweekday(6)
    next_month_cal = cal.monthcalendar(next_month.year, next_month.month)
    
    basecal = list(itertools.chain.from_iterable(next_month_cal)) #一次元
    daysrange = max(basecal)
    wedls = []
    c = 7
    for i in basecal[3:]:
        if c == 7:
            wedls.append(i)
            c = 0
        c += 1
    listcal = map(num_to_list,basecal)
    listcal = list(listcal) #basecalのすべての要素を[]で括った
    data = Profile.objects.filter(Q(days__isnull = False) | Q(days_late__isnull = False))
    if len(data) == 0:
        param = {
            'shift' : [],
            'nls' : "",
        }
        return render(request, 'shiftapp/shift.html', param)

    member_list = []
    gender_dic = dict()
    for d in data:
        name = d.name
        member_list.append(name)
        gender = d.gender
        gender_dic[name] = gender
        gender_dic['*'+name] = gender
    baseshift = make_baseshift(data)
    baseshift[0] = []
    for i in wedls:
        baseshift[i] = []
    
    for bs, i in zip(baseshift, range(len(baseshift))):
        if i > daysrange:
            baseshift[i] = []
        else:
            baseshift[i] = member_to_pair(bs, gender_dic)
    best_shift, nls = choiceshift(baseshift, member_list)
    
    for calday, i in zip(listcal, range(len(listcal))):
        if listcal[i] == [0]:
            listcal[i] = ""
        elif len(best_shift[listcal[i][0]]) == 0:
            listcal[i] = str(listcal[i][0])
        elif len(best_shift[listcal[i][0]]) == 1:
            listcal[i] = str(listcal[i][0]) + ': '+ best_shift[listcal[i][0]][0]
        elif len(best_shift[listcal[i][0]]) == 2:
            listcal[i] = str(listcal[i][0]) + ': ' + best_shift[listcal[i][0]][0] + ',' + best_shift[listcal[i][0]][1]


    shift = [listcal[i:i+7] for i in range(0,len(listcal),7)]
    param = {
        'shift' : shift,
        'nls' : nls,
    }
    
    return render(request, 'shiftapp/shift.html', param)
    
