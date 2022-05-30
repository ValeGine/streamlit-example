import networkx as nx
import numpy
import random
import math 

class TemporalGraph:
    
    def __init__(self, fileInput, storeGraph=True, networkx=False):
        infile = open(fileInput, "r")
        if storeGraph:
            if networkx:
                g = nx.DiGraph()
                l = []
                for aline in infile:
                    bline = aline[:-1]
                    s = bline.split(" ")
                    g.add_edge(s[0], s[1])
                    g[s[0]][s[1]][s[2]]=s[3]
                    l.append((int(s[0]),int(s[1]),int(s[2]),int(s[3])))
            else:
                g = nx.DiGraph()
                dizEdge = {}
                l = []
                for aline in infile:
                    bline = aline[:-1]
                    s = bline.split(" ")
                    g.add_edge(s[0], s[1])
                    edge = tuple(s[0:2])
                    s_time = tuple(s[2:4])
                    if edge not in dizEdge:
                        dizEdge[edge] = [s_time]
                    else:
                        dizEdge[edge].append(s_time)
                    l.append((int(s[0]),int(s[1]),int(s[2]),int(s[3])))
                self.diz = dizEdge
            self.graph = g
            self.listOfEdges = l
        else:
            self.fileInput = fileInput
        self.isStored = storeGraph
        infile.close()

    
    def get_time_interval(self):
        t_alpha = self.listOfEdges[0][2]
        t_omega = self.listOfEdges[-1][2]
        return (t_alpha, t_omega)
    
    def get_number_of_nodes(self):
        return self.graph.number_of_nodes()
        

    def earliest_arrival_time(self, x, t_alpha=None, t_omega=None):
        if t_alpha == None:
            t_alpha = self.get_time_interval()[0]
        if t_omega == None:
            t_omega = self.get_time_interval()[1]
        # x: integer
        e_a_t = [numpy.inf]*self.graph.number_of_nodes()
        e_a_t[x] = t_alpha
        stop = False
        i = 0
        while not stop:
            (u,v,t,z) = self.listOfEdges[i] 
            if t >= e_a_t[u] and (t+z) <= t_omega:
                if t+z < e_a_t[v]:
                    e_a_t[v] = t+z
            else:
                if t >= t_omega:
                    stop = True 
            i = i + 1
        return e_a_t 
    
    
    def latest_departure_time(self, x, t_alpha=None, t_omega=None):
        if t_alpha == None:
            t_alpha = self.get_time_interval()[0]
        if t_omega == None:
            t_omega = self.get_time_interval()[1]
        # x: integer
        l_d_t = [-(numpy.inf)]*self.graph.number_of_nodes()
        l_d_t[x] = t_omega
        stop = False
        i = (len(self.listOfEdges) - 1)
        while not stop and i >= 0:
            (u,v,t,z) = self.listOfEdges[i]
            if t >= t_alpha:
                if t+z <= l_d_t[v]:
                    if t > l_d_t[u]:
                        l_d_t[u] = t 
            else:
                stop = True
            i = i - 1
        return l_d_t

    
    def fastest_path(self, x, t_alpha=None, t_omega=None):
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
    
    
    def shortest_path(self, x, t_alpha=None, t_omega=None):
        if t_alpha == None:
            t_alpha = self.get_time_interval()[0]
        if t_omega == None:
            t_omega = self.get_time_interval()[1]
        # x: integer
        list_of_sorted_lists = [[]]*self.graph.number_of_nodes() 
        distances = [numpy.inf]*self.graph.number_of_nodes()
        distances[x] = 0
        stop = False
        i = 0
        while not stop:
            (u,v,t,z) = self.listOfEdges[i]
            if t >= t_alpha and (t+z) <= t_omega:
                if u == x:
                    if (0,t) not in list_of_sorted_lists[x]:
                        list_of_sorted_lists[x].append((0,t))
                if list_of_sorted_lists[u]:
                    find_elem = False
                    j = 0
                    while not find_elem and j < len(list_of_sorted_lists[u]):
                        elem_u = list_of_sorted_lists[u][j]
                        if elem_u[1] <= t:
                            new_d = elem_u[0] + z
                            new_arrival_time = t + z
                            inserted_new = False  
                            if not list_of_sorted_lists[v]:  
                                list_of_sorted_lists[v].append((new_d, new_arrival_time))
                                inserted_new = True
                            else: 
                                same_arrival_time = False
                                for k, elem_v in enumerate(list_of_sorted_lists[v]):
                                    if elem_v[1] == new_arrival_time:
                                        if elem_v[0] > new_d:
                                            list_of_sorted_lists[v][k] = (new_d, new_arrival_time)
                                            inserted_new = True
                                        same_arrival_time = True
                                if not same_arrival_time:
                                    new_is_dominated = False
                                    n  = 0
                                    while not new_is_dominated and n < len(list_of_sorted_lists[v]):
                                        elem_v = list_of_sorted_lists[v][n]
                                        if (elem_v[0] < new_d and elem_v[1] <= new_arrival_time) or (
                                            elem_v[0] == new_d and elem_v[1] < new_arrival_time):
                                            new_is_dominated = True
                                        else:
                                            n +=1
                                    if not new_is_dominated:
                                        list_of_sorted_lists[v].append((new_d, new_arrival_time))
                                        inserted_new = True
                            if inserted_new:
                                list_of_sorted_lists[v][:] = [e for e in list_of_sorted_lists[v] if not (
                                        (e[0] > new_d and e[1] >= new_arrival_time) or
                                        (e[0] == new_d and e[1] > new_arrival_time))]
                                if new_d < distances[v]:
                                    distances[v] = new_d
                                list_of_sorted_lists[v].sort(key=lambda tup: tup[1], reverse=True)
                            find_elem = True
                        if not find_elem:
                            j +=1
            else:
                if t >= t_omega:
                    stop = True
            i += 1
        return distances
    
        
    def approximate_average_eat(self, eps, t_alpha=None, t_omega=None):  
        if t_alpha == None:
            t_alpha = self.get_time_interval()[0]
        if t_omega == None:
            t_omega = self.get_time_interval()[1]
        # eps: float, k: integer
        k = int(math.log(self.graph.number_of_nodes())/(eps**2))
        tot_average = 0
        sample_of_nodes = []
        for i in range(k):
            sample_of_nodes.append(random.randrange(0,self.graph.number_of_nodes()))
        for node in sample_of_nodes:
            a = self.earliest_arrival_time(node, t_alpha, t_omega)
            tot=[]
            for i in range(len(a)):
                if a[i] < numpy.inf:
                    tot.append(a[i])
            tot_average += (sum(tot)/len(tot))
        absolute_error = 2 * math.exp(-2*k*(eps**2))
        return tot_average/self.graph.number_of_nodes(), absolute_error
    
      
    def approximate_average_ldt(self, eps, t_alpha=None, t_omega=None):  
          if t_alpha == None:
              t_alpha = self.get_time_interval()[0]
          if t_omega == None:
              t_omega = self.get_time_interval()[1]
          # eps: float, k: integer
          k = int(math.log(self.graph.number_of_nodes())/(eps**2))
          tot_average = 0
          sample_of_nodes = []
          for i in range(k):
              sample_of_nodes.append(random.randrange(0,self.graph.number_of_nodes()))
          for node in sample_of_nodes:
              a = self.latest_departure_time(node, t_alpha, t_omega)
              tot=[]
              for i in range(len(a)):
                  if a[i] > -(numpy.inf):
                      tot.append(a[i])
              tot_average += (sum(tot)/len(tot))
          absolute_error = 2 * math.exp(-2*k*(eps**2))
          return tot_average/self.graph.number_of_nodes(), absolute_error
               
 
    def not_connected(self, t_alpha=None, t_omega=None):
        if t_alpha == None:
            t_alpha = self.get_time_interval()[0]
        if t_omega == None:
            t_omega = self.get_time_interval()[1]
        average_not_connected=[] 
        for node in range(self.graph.number_of_nodes()):
           tot=0
           eat=self.earliest_arrival_time(node)
           for i in eat:
               if i==numpy.inf:
                   tot+=1
           average_not_connected.append(tot)
        return (sum(average_not_connected)/len(average_not_connected))
 
bel ="belfast-weighted-sorted.txt"



belfast=TemporalGraph(bel) 


a=belfast.not_connected()

