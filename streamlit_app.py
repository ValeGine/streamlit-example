
        if t_alpha == None:
            t_alpha = self.get_time_interval()[0]
        if t_omega == None:
            t_omega = self.get_time_interval()[1]
        # x: integer
        list_of_sorted_lists = [[]]*self.graph.number_of_nodes()     #inizializzo L_v che in ogni posizione (per ogni nodo) ha una lista di elementi del genere (starting_time, arrival_time)
        fastest = [numpy.inf]*self.graph.number_of_nodes()
        fastest[x] = 0
        for (u,v,t,z) in self.listOfEdges:                           #listOfEdges() contiene la lista di archi ordinati per tempo t crescente
            if t >= t_alpha and (t+z) <= t_omega:
                if u == x:                                           #se troviamo un arco che parte dal nodo sorgente
                    if (t,t) not in list_of_sorted_lists[x]:         #ed è ancora vuoto, allora ci inserisco il path da lui a se stesso (t,t)
                        list_of_sorted_lists[x].append((t,t))
                if list_of_sorted_lists[u]:                          #check che la lista per il nodo u non sia vuota (altrimenti non posso prolungare il path fino a v)
                    for elem_u in list_of_sorted_lists[u]:           #Voglio trovare un path che parte da u 
                        if elem_u[1] <= t:                           #che abbia tempo di arrivo ad u minore del tempo di partenza dell'arco (u,v,t,z)
                            new_starting_time = elem_u[0]            #se lo trovo creo il prolungamento da inserire evetualmente in v (starting_time_di_u, t+z)
                            new_arrival_time = t + z
                            inserted_new = False
                            if not list_of_sorted_lists[v]:          #se la lista in v è vuota allora loinserisco perchè sicuramente non è dominato
                                list_of_sorted_lists[v].append((new_starting_time, new_arrival_time))
                                inserted_new = True
                            else:                                    #se la lista di v non è vuota significo che ho altri path per v trovati e devo controllare se posso inserirlo
                                same_starting_time = False           
                                for k, elem_v in enumerate(list_of_sorted_lists[v]):    #controllo se c'è già un elemento con stesso starting_time
                                    if elem_v[0] == new_starting_time:
                                        if elem_v[1] > new_arrival_time:                #sostituisco direttamente il new_arrival se è più piccolo nell'elemento con stesso starting time
                                            list_of_sorted_lists[v][k] = (new_starting_time, new_arrival_time)
                                            inserted_new = True
                                        same_starting_time = True
                                        break
                                if not same_starting_time:           #se non c'è un elemento con stesso starting time devo controllare se è dominato
                                    new_is_dominated = False
                                    for elem_v in list_of_sorted_lists[v]:
                                        if (elem_v[0] > new_starting_time and elem_v[1] <= new_arrival_time) or (    #se valgono le condizioni il nuovo elemento è dominato
                                            elem_v[0] == new_starting_time and elem_v[1] < new_arrival_time):
                                            new_is_dominated = True
                                            break
                                    if not new_is_dominated:         #se non è dominato lo inserisco
                                        list_of_sorted_lists[v].append((new_starting_time, new_arrival_time))
                                        inserted_new = True
                            if inserted_new:                        #se ho inserito il nuovo path per v (prolungato da u) devo vedere se gli elementi già presenti in v sono dominati dal nuovo elemento
                                list_of_sorted_lists[v][:] = [e for e in list_of_sorted_lists[v] if not (        #tengo nella lista solo gli elementi che non sono dominati (controllo stesse condizioni di prima))
                                        (e[0] < new_starting_time and e[1] >= new_arrival_time) or
                                        (e[0] == new_starting_time and e[1] > new_arrival_time))]
                                if (new_arrival_time - new_starting_time) < fastest[v]:       #se ho inserito il nuovo path in v controllo se è più veloce di quello trovato fino ad adesso
                                    fastest[v] = new_arrival_time - new_starting_time
                                list_of_sorted_lists[v].sort(key=lambda tup: tup[1], reverse=True)   #ordino per tempo di arrivo così che quando cerco il path di u con 
                                #cui prolungare (riga 121-123) prendo quello con arrival time più alto (di conseguenza anche starting time + alto) che assicura path più veloce
                            break
            else:
                if t >= t_omega:
                    break
        return fastest
    
 
bel ="belfast-weighted-sorted.txt"



belfast=TemporalGraph(bel) 


a=belfast.not_connected()

