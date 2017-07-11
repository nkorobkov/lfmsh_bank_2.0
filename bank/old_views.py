@permission_required('bank.add_transaction', login_url='bank:index')
def add_mass_special(request):
    print(request.user.account)
    if request.method == "POST":
        print(request.POST['type'])

        fac_attendants = []
        form = SprecialTransForm(request.POST)

        for u in User.objects.filter(groups__name='pioner'):
            if u.username + '_num' in request.POST and request.POST[u.username + '_num']:
                fac_attendants.append((u, request.POST[u.username + '_num']))

        if not fac_attendants:
            return redirect(reverse('bank:index'))

        creator = request.user

        description = request.POST['description']
        type = TransactionType.objects.get(pk=request.POST['type'])

        print(type)
        status = TransactionState.objects.get(name='PR')
        new_transactions = []
        for u, s in fac_attendants:
            new_trans = Transaction.create_trans(recipient=u, value=int(s), creator=creator, description=description,
                                                 type=type, status=status)
            new_transactions.append(new_trans)
        if new_transactions:
            return render(request, 'bank/add_trans/trans_add_ok.html', {'transactions': new_transactions})
        else:
            users = User.objects.filter(groups__name='pioner')
            return render(request, 'bank/add_trans/trans_add_mass_special.html', {'users': users})





    else:
        users = {}
        users['1'] = User.objects.filter(groups__name='pioner').filter(account__otr=1).order_by('last_name')
        users['2'] = User.objects.filter(groups__name='pioner').filter(account__otr=2).order_by('last_name')
        users['3'] = User.objects.filter(groups__name='pioner').filter(account__otr=3).order_by('last_name')
        users['4'] = User.objects.filter(groups__name='pioner').filter(account__otr=4).order_by('last_name')

        form = SprecialTransForm()

        return render(request, 'bank/add_trans/trans_add_mass_special.html', {'users': users, 'form': form})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_exam(request, meta_link_pk=None):
    if request.method == "POST":
        print(request.POST)

        exam_attendants = []
        sum_score = 0
        for u in User.objects.filter(groups__name='pioner'):
            if str(u.pk) in request.POST and request.POST[str(u.pk)]:
                exam_attendants.append((u, request.POST[str(u.pk)]))
                sum_score += (max(0, int(request.POST[str(u.pk)]))) ** (0.5)

        if not exam_attendants:
            return redirect(reverse('bank:index'))

        num_of_attendants = len(exam_attendants)
        budget = int(request.POST['budget'])

        creator = request.user
        description = request.POST['description']
        type = TransactionType.objects.get(name='lec')

        print(type)
        status = TransactionState.objects.get(name='PR')
        new_transactions = []
        meta_link = Transaction.create_trans(recipient=None, value=BUDGET * num_of_attendants, creator=creator,
                                             description=description,
                                             type=type, status=status)
        meta_link.save()
        meta = MetaTransaction(meta=meta_link, creation_dict=dict(request.POST).__repr__())
        meta.save()

        for u, s in exam_attendants:
            new_trans = Transaction.create_trans(recipient=u, value=hf.lec(s, sum_score, budget, num_of_attendants),
                                                 creator=creator, description=description,
                                                 type=type, status=status)
            new_transactions.append(new_trans)
            meta.transactions.add(new_trans)

        return render(request, 'bank/add_trans/trans_add_ok.html', {'transactions': new_transactions})





    else:
        users = {}
        users['1'] = User.objects.filter(groups__name='pioner').filter(account__otr=1).order_by('last_name')
        users['2'] = User.objects.filter(groups__name='pioner').filter(account__otr=2).order_by('last_name')
        users['3'] = User.objects.filter(groups__name='pioner').filter(account__otr=3).order_by('last_name')
        users['4'] = User.objects.filter(groups__name='pioner').filter(account__otr=4).order_by('last_name')

        if meta_link_pk:
            meta_link = Transaction.objects.get(pk=meta_link_pk)
            creation_dict = eval(MetaTransaction.objects.get(meta=meta_link).creation_dict)

        else:
            creation_dict = {}
        print(creation_dict)
        c_d = {}
        for user_pk in range(1000):
            if str(user_pk) in creation_dict and creation_dict[str(user_pk)][0]:
                c_d[user_pk] = int(creation_dict[str(user_pk)][0])
        users_pk = {'1': [], '2': [], '3': [], '4': [], '0': [], '5': []}
        for i in range(1000):
            if User.objects.filter(pk=i) and i in c_d:
                users_pk[str(User.objects.filter(pk=i)[0].account.otr)].append(i)

        print('users pk', users_pk)
        print('creation dict', c_d)
        form = SprecialTransForm()

        return render(request, 'bank/add_trans/trans_add_exam.html',
                      {'users': users, 'users_pk': users_pk, 'table': 'bank/add_trans/otr_tables/exam_table.html',
                       'form': form,
                       'budget': BUDGET, 'creation_dict': c_d})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_zaryadka(request, meta_link_pk=None):
    if request.method == "POST":

        zar_attendants = []

        for u in User.objects.filter(groups__name='pioner'):
            if u.username in request.POST:
                zar_attendants.append(u)

        if not zar_attendants:
            return redirect(reverse('bank:index'))

        value = hf.zaryadka(len(zar_attendants))
        description = request.POST['description']
        creator = request.user
        type = TransactionType.objects.get(name='zaryadka')

        status = TransactionState.objects.get(name='PR')

        new_transactions = []
        meta_link = Transaction.create_trans(recipient=None, value=ZARYADKA_BUDGET, creator=creator,
                                             description=description,
                                             type=type, status=status)
        meta_link.save()
        meta = MetaTransaction(meta=meta_link, creation_dict=dict(request.POST).__repr__())
        meta.save()

        for u in zar_attendants:
            new_trans = Transaction.create_trans(recipient=u, value=value, creator=creator, description=description,
                                                 type=type, status=status)
            new_transactions.append(new_trans)
            meta.transactions.add(new_trans)

        if new_transactions:
            return render(request, 'bank/add_trans/trans_add_ok.html', {'transactions': new_transactions})

        else:
            users = User.objects.filter(groups__name='pioner')
            return render(request, 'bank/add_trans/trans_add_zaryadka.html', {'users': users})
    else:  # request method get
        # render table with info from metatrans (pk = meta_pk).creation_dict

        table = []
        for i in range(4):
            table.append(
                ZarTable(User.objects.filter(groups__name='pioner').filter(account__otr=i + 1), order_by='name'))
            RequestConfig(request).configure(table[i])
            table[i].paginate(per_page=1000)

        if meta_link_pk:
            meta_link = Transaction.objects.get(pk=meta_link_pk)
            creation_dict = eval(MetaTransaction.objects.get(meta=meta_link).creation_dict)

        else:
            creation_dict = {}
        # creation_dict = {k : int(creation_dict[k][0]) for k in creation_dict}

        return render(request, 'bank/add_trans/trans_add_zaryadka.html',
                      {'table': table, 'creation_dict': creation_dict})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_lec(request):
    if request.method == "POST":
        print(request.POST)

        lec_missers = []
        description = request.POST['description']
        creator = request.user
        type = TransactionType.objects.get(name='fine_lec')
        att_type = TransactionType.objects.get(name='lec_attend')

        status = TransactionState.objects.get(name='PR')
        att_val = 10311100
        attends = []
        for u in User.objects.filter(groups__name='pioner'):
            if u.username not in request.POST:
                lec_missers.append(u)
            else:
                a = Transaction.create_trans(recipient=u, value=att_val, creator=creator, description=description,
                                             type=att_type, status=status)
                attends.append(a)
                print(u.username)

        if not lec_missers:
            return redirect(reverse('bank:index'))

        new_transactions = []
        for u in lec_missers:
            new_trans = Transaction.create_trans(recipient=u, value=hf.lec_pen(u.account.lec_missed), creator=creator,
                                                 description=description,
                                                 type=type, status=status)
            new_transactions.append(new_trans)

        return render(request, 'bank/add_trans/trans_add_ok.html',
                      {'transactions': new_transactions, 'attends': attends})



    else:

        table = []
        for i in range(4):
            table.append(
                LecTable(User.objects.filter(groups__name='pioner').filter(account__otr=i + 1), order_by='name'))
            RequestConfig(request).configure(table[i])
            table[i].paginate(per_page=1000)

        return render(request, 'bank/add_trans/trans_add_lec.html', {'table': table})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_fac(request):
    if request.method == "POST":
        print(request.POST)

        fac_attendants = []

        for u in User.objects.filter(groups__name='pioner'):
            if u.username + '_num' in request.POST and request.POST[u.username + '_num']:
                fac_attendants.append((u, request.POST[u.username + '_num']))

        if not fac_attendants:
            return redirect(reverse('bank:index'))

        description = request.POST['description']
        creator = request.user
        type = TransactionType.objects.get(name='fac_pass')

        status = TransactionState.objects.get(name='PR')

        new_transactions = []
        for u, s in fac_attendants:
            new_trans = Transaction.create_trans(recipient=u, value=int(s), creator=creator, description=description,
                                                 type=type, status=status)
            new_transactions.append(new_trans)

        if new_transactions:
            return render(request, 'bank/add_trans/trans_add_ok.html', {'transactions': new_transactions})

        else:
            users = User.objects.filter(groups__name='pioner')
            return render(request, 'bank/add_trans/trans_add_fac.html', {'users': users})
    else:
        users = {}
        users['1'] = User.objects.filter(groups__name='pioner').filter(account__otr=1).order_by('last_name')
        users['2'] = User.objects.filter(groups__name='pioner').filter(account__otr=2).order_by('last_name')
        users['3'] = User.objects.filter(groups__name='pioner').filter(account__otr=3).order_by('last_name')
        users['4'] = User.objects.filter(groups__name='pioner').filter(account__otr=4).order_by('last_name')

        return render(request, 'bank/add_trans/trans_add_fac.html',
                      {'users': users, 'table': 'bank/add_trans/otr_tables/fac_table.html', 'list': [1, 2, 3, 4]})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_activity(request):
    if request.method == "POST":

        participants = {1: [], 2: [], 3: [], 4: []}
        f = 0

        for u in User.objects.filter(groups__name='pioner'):
            if str(u.pk) + '_place' in request.POST and request.POST[str(u.pk) + '_place'] and int(
                    request.POST[str(u.pk) + '_place']) != 5:
                f = 1
                participants[int(request.POST[str(u.pk) + '_place'])].append(u)

        if not f:
            return redirect(reverse('bank:index'))

        description = request.POST['description']
        creator = request.user
        type = TransactionType.objects.get(name=request.POST['type'])

        status = TransactionState.objects.get(name='PR')
        activity_money = {1: int(request.POST['1m']), 2: int(request.POST['2m']), 3: int(request.POST['3m']),
                          4: int(request.POST['4m'])}
        new_transactions = []
        for p in participants:

            for u in participants[p]:
                new_trans = Transaction.create_trans(recipient=u, value=activity_money[p], creator=creator,
                                                     description=description,
                                                     type=type, status=status)
                new_transactions.append(new_trans)

        if new_transactions:
            return render(request, 'bank/add_trans/trans_add_ok.html', {'transactions': new_transactions})

        else:
            users = User.objects.filter(groups__name='pioner')
            return render(request, 'bank/add_trans/trans_add_activity.html', {'users': users})
    else:
        users = {}
        users['1'] = User.objects.filter(groups__name='pioner').filter(account__otr=1).order_by('last_name')
        users['2'] = User.objects.filter(groups__name='pioner').filter(account__otr=2).order_by('last_name')
        users['3'] = User.objects.filter(groups__name='pioner').filter(account__otr=3).order_by('last_name')
        users['4'] = User.objects.filter(groups__name='pioner').filter(account__otr=4).order_by('last_name')

        return render(request, 'bank/add_trans/trans_add_activity.html',
                      {'users': users, 'table': 'bank/add_trans/otr_tables/activity_table.html', 'list': [1, 2, 3, 4],
                       'activity': ACTIVITY_MONEY})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_sem(request):
    if request.method == "POST":
        print(request.POST)
        form = SeminarTransForm(request.POST)
        if form.is_valid():

            score = 0
            for i in range(9):
                score += int(request.POST['m' + str(i + 1)])

            value = hf.seminar(score)
            recipient = form.cleaned_data['recipient'].user
            description = request.POST['description']
            creator = request.user
            type = TransactionType.objects.get(name='sem')
            status = TransactionState.objects.get(name='PR')

            att_val = 1000000 * (int(form.cleaned_data['date'].year) % 100) + 10000 * (
                int(form.cleaned_data['date'].month)) + 100 * (int(form.cleaned_data['date'].day)) + int(
                request.POST['block'])
            print(att_val)
            att_type = TransactionType.objects.get(name='sem_attend')

            new_trans = Transaction.create_trans(recipient=recipient, value=value, creator=creator,
                                                 description=description,
                                                 type=type, status=status)
            attends = []
            for u in User.objects.filter(groups__name='pioner'):
                if u.username in request.POST and request.POST[u.username]:
                    a = Transaction.create_trans(recipient=u, value=att_val, creator=creator,
                                                 description=description,
                                                 type=att_type, status=status)

                    if a.counted:
                        attends.append(a)

            return render(request, 'bank/add_trans/trans_add_ok.html',
                          {'transactions': [new_trans], 'attends': attends})
        else:
            table = []
        for i in range(4):
            table.append(
                ZarTable(User.objects.filter(groups__name='pioner').filter(account__otr=i + 1), order_by='name'))
            RequestConfig(request).configure(table[i])
            table[i].paginate(per_page=1000)
        form = SeminarTransForm(request.POST)
        return render(request, 'bank/add_trans/trans_add_seminar.html',
                      {'form': form, 'table_html': 'bank/add_trans/otr_tables/check_table.html', 'table': table})



    else:
        table = []
        for i in range(4):
            table.append(
                ZarTable(User.objects.filter(groups__name='pioner').filter(account__otr=i + 1), order_by='name'))
            RequestConfig(request).configure(table[i])
            table[i].paginate(per_page=1000)
        form = SeminarTransForm()
        return render(request, 'bank/add_trans/trans_add_seminar.html',
                      {'form': form, 'table_html': 'bank/add_trans/otr_tables/check_table.html', 'table': table})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_fac_att(request):
    if request.method == "POST":
        print(request.POST)
        form = FacAttTransForm(request.POST)
        if form.is_valid():

            description = request.POST['description']
            creator = request.user
            status = TransactionState.objects.get(name='PR')

            att_val = 1000000 * (int(form.cleaned_data['date'].year) % 100) + 10000 * (
                int(form.cleaned_data['date'].month)) + 100 * (int(form.cleaned_data['date'].day)) + int(
                request.POST['block']) + 10
            att_type = TransactionType.objects.get(name='fac_attend')

            attends = []
            for u in User.objects.filter(groups__name='pioner'):
                if u.username in request.POST and request.POST[u.username]:
                    a = Transaction.create_trans(recipient=u, value=att_val, creator=creator,
                                                 description=description,
                                                 type=att_type, status=status)
                    print(u.username + 'check')
                    attends.append(a)

            return render(request, 'bank/add_trans/trans_add_ok.html', {'attends': attends})
        else:
            table = []
        for i in range(4):
            table.append(
                ZarTable(User.objects.filter(groups__name='pioner').filter(account__otr=i + 1), order_by='name'))
            RequestConfig(request).configure(table[i])
            table[i].paginate(per_page=1000)
        form = SeminarTransForm(request.POST)
        return render(request, 'bank/add_trans/trans_add_fac_att.html',
                      {'form': form, 'table_html': 'bank/add_trans/otr_tables/check_table.html', 'table': table})



    else:
        table = []
        for i in range(4):
            table.append(
                ZarTable(User.objects.filter(groups__name='pioner').filter(account__otr=i + 1), order_by='name'))
            RequestConfig(request).configure(table[i])
            table[i].paginate(per_page=1000)
        form = SeminarTransForm()
        return render(request, 'bank/add_trans/trans_add_fac_att.html',
                      {'form': form, 'table_html': 'bank/add_trans/otr_tables/check_table.html', 'table': table})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_fine(request):
    if request.method == "POST":

        form = FineTransForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']

            recipient = form.cleaned_data['recipient'].user
            description = form.cleaned_data['description']
            creator = request.user

            type = form.cleaned_data['type']
            status = TransactionState.objects.get(name='PR')

            new_trans = Transaction.create_trans(recipient=recipient, value=value, creator=creator,
                                                 description=description,
                                                 type=type, status=status)

            return render(request, 'bank/add_trans/trans_add_ok.html', {'transactions': [new_trans]})
        return render(request, 'bank/add_trans/trans_add_fine.html', {'form': form})


    else:

        form = FineTransForm()
        return render(request, 'bank/add_trans/trans_add_fine.html', {'form': form})


@permission_required('bank.add_transaction', login_url='bank:index')
def add_lab(request):
    if request.method == "POST":

        form = LabTransForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            recipient = form.cleaned_data['recipient'].user
            description = form.cleaned_data['description']
            creator = request.user

            type = TransactionType.objects.get(name='lab_pass')
            status = TransactionState.objects.get(name='PR')

            new_trans = Transaction.create_trans(recipient=recipient, value=value, creator=creator,
                                                 description=description,
                                                 type=type, status=status)

            return render(request, 'bank/add_trans/trans_add_ok.html', {'transactions': [new_trans]})
        return render(request, 'bank/add_trans/trans_add_lab.html', {'form': form})


    else:

        form = LabTransForm()
        return render(request, 'bank/add_trans/trans_add_lab.html', {'form': form})


@permission_required('bank.add_p2p_transaction', login_url='bank:index')
def add_p2p(request):
    if request.method == "POST":

        form = P2PTransForm(int(request.user.account.balance - hf.p2p_buf), request.POST)
        # form.fields['value'].max_value = int((request.user.account.balance * hf.p2p_proc))
        # print form.fields['value']


        if form.is_valid():
            value = form.cleaned_data['value']
            recipient = form.cleaned_data['recipient'].user
            description = form.cleaned_data['description']
            creator = request.user

            type = TransactionType.objects.get(name='p2p')
            status = TransactionState.objects.get(name='AD')

            new_trans = Transaction.create_trans(recipient=recipient, value=value, creator=creator,
                                                 description=description, type=type, status=status)

            return render(request, 'bank/add_trans/trans_add_p2p_ok.html', {'a': new_trans})
        return render(request, 'bank/add_trans/trans_add_p2p.html', {'form': form})


    else:

        form = P2PTransForm(int((request.user.account.balance - hf.p2p_buf)))
        form.fields['recipient'].queryset = form.fields['recipient'].queryset.exclude(user=request.user)

        print(form.fields['value'].max_value)

        return render(request, 'bank/add_trans/trans_add_p2p.html', {'form': form})