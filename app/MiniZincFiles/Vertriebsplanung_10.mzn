int: nproducts; 
set of int: Products = 1..nproducts;  
int: nsites; 
set of int: Sites = 1..nsites;  
int: ncustomers; 
set of int: Customers = 1..ncustomers;

  
% Bezeichnung der Produkte, Nachfragemärkte und Werke     
array[Products] of string: pname; 
array[Customers] of string: cname; 
array[Sites] of string: sname; 

%Ergebnisbeitrag eines Produktes p in einem Nachfragemarkt c
array[Customers, Products] of int: eb;
%Gewicht eines Produktes p
array[Products] of int: weight;
%Supercredit für das jeweilige Produkt, 2 falls C02 Ausstoß geringer als 50g CO2/km, sonst 1
array[Products] of int: supercredit;
%Maximale Produktionskapazität für das jeweilige Werk s 
array[Sites] of int: maxProduction;
%Die Nachfrage je Nachfragebereich c nach dem jweiligen Produkt p
array[Customers, Products] of int: demand;
%Die mögliche Steigerung der Nachfrage des Produktes p
array[Products] of float: excessdemand;
%Der gemessene WLTP Wert des Produktes p
array[Products] of int: emissionWLTP;
%Die Strafzahlung für jedes überschüssigge Gramm C02
int: payperfine;
% Der Produktionsplan der einzelnen Werke und Fahrzeuge: 1, 
% falls das Produkt p in Werk s hergestellt werden kann, sonst 0
array[Sites, Products] of int: productionPlan;


%%%%%%%%%%%%%%__________________________Entscheidungsvariablen______________________%%%%%%%%%%%%%%%%%%%%%%

%Anzahl an Produkten p, die von Werk s and Nachfragebereich c geliefert werden
array[Sites, Customers, Products] of var int: delivered;
%Anzahl an Produkten p, die in Werk s produziert werden
array[Sites, Products] of var int: produce;
%Verkaufte Anzahl an Fahrzeugen je Produkt
array[Products] of var int: soldCars;
%Anzahl an Produkten, welche durch jedes Werk s verkauft werden
array[Sites] of var int: soldCarsPerSite;
%Gesamter Profit
var int: totalSales;
%Profit der einzelnen Produkte
array[Products] of var int: totalSales_perProduct;
%Profit der einzelnen Produkte
array[Customers] of var int: totalSales_perCustomer;
%Anzahl an Produkten p, die in Werk s produziert werden
array[Products] of var int: demand_per_Product;
%Summe der verkauften Fahrzeuge inklusive der Faktoren der Supercredits
var int: carsforWLTP_supercredit;
%Gesamte Anzahl an produzierten Fahrzeugen
var int: sold; 
%Gesamte Anzahl an ausgelieferten Fahrzeugen
var int: delivered_total;
%Ausgestoßene Emissionen der Fahrzeugflotte
var int: emission;
%Verursachte Emissionen der Fahrzeugflotte bestehend aus nur einem Produkt
array[Products] of var int: emissionPerCar;
%Gesamtergebnis des Automobilherstellers
var float: total;
%Emissionsgrenzwert, welcher nicht überschritten werden soll.
var float: emissionlimit;
%Durchschnittliches Gewicht der Fahrzeugflotte
var float: avgweight;
%Gesamtgewicht der Fahrzeugflotte
var float: totalweight;
%Durchschnittlicher WLTP-Wert der Fahrzeugflotte
var 0.00..300.00: wltpavg;
%Strafzahlungen durch Überschreitung der WLTP Grenze
var float: emissionRealFine;
%Differenz zwischen wltpavg und emissionlimit
var 0.00..300.00: wltpdif;
%Kann vernachlässigt werden
var float: emissiongoal;


%%%%%%%%%%%%%%%%%%%_________Constraints____________%%%%%%%%%%%%%%%%%%%%%%%%%
constraint wltpdif = (wltpavg - emissionlimit);

%Produkte p können nur dann an einem Werk s produziert werden, wenn der Produktionsplan an der jeweiligen Stelle eine 1 aufweist.
constraint forall(s in Sites)(
                forall(p in Products)(
                      (if productionPlan[s,p] <= 0 then produce[s,p] = 0  else produce[s,p] > 0 endif)));
                  
%DieAnzahlderproduziertensowiegeliefertenProduktenkannnichtnegativ sein.                 
constraint forall(s in Sites, c in Customers, p in Products)(delivered[s,c,p] >= 0);
constraint forall(s in Sites, p in Products)(produce[s,p] >= 0);

%Für jedes Werk s gilt, dass sowohl die dort produzierten Produkte p sowie die gelieferten Produkte p von Werk s zum Kundenbereich c nicht die maximale Produktionskapazität eines Werkes übersteigen.
constraint forall(s in Sites)(sum(p in Products)(produce[s,p]) <= maxProduction[s]);
constraint forall(s in Sites)(sum(c in Customers, p in Products)(delivered[s,c,p]) <= maxProduction[s]);
                       
%Für jedes Produkt p muss gelten, dass die Summe dieser produzierten sowie gelieferten Produkte größer ist, als die gesamte Nachfrage eines Produktes.                       
constraint forall(p in Products) ((sum(s in Sites)(produce[s, p])) >= (sum(c in Customers) (demand[c,p])));
constraint forall(p in Products) ((sum(s in Sites, c in Customers)(delivered[s,c,p])) >= (sum(c in Customers)(demand[c,p])));
constraint forall(c in Customers, p in Products) ((sum(s in Sites)(delivered[s,c,p])) >= (demand[c,p]));

%Für jedes Werk s gilt, dass sowohl die produzierten Produkte p in Werk s sowie die gelieferten Produkte p von Werk s zum Kundenbereich c nicht die mögliche überschüssige Nachfrage eines Produktes p übersteigen kann.
constraint forall(p in Products) ((sum(s in Sites)(produce[s, p])) <= round((sum(c in Customers)((demand[c,p])) * excessdemand[p])));
constraint forall(p in Products) ((sum(s in Sites, c in Customers)(delivered[s,c,p])) <= round((sum(c in Customers)((demand[c,p])) * excessdemand[p])));

%Die Summe der produzierten Fahrzeuge entspricht der Summe der ausgelieferten Fahrzeuge.
constraint forall(s in Sites, p in Products)((produce[s,p] * productionPlan[s,p]) = sum(c in Customers)(delivered[s,c,p]));
constraint sum(s in Sites, c in Customers, p in Products)(delivered[s,c,p]) = sum(s in Sites, p in Products)(produce[s,p]);

%Zuweisung der Variablen soldCars und soldCarsPerSite.
constraint forall(p in Products)(soldCars[p] = (sum(s in Sites)(produce[s,p])));
constraint forall(s in Sites)(soldCarsPerSite[s] = (sum(p in Products)(produce[s,p])));
%Zuweisung der Variablen demandPerProduct.
constraint forall(p in Products) (demand_per_Product[p] = sum(c in Customers) (demand[c,p]));

%Es müssen mindestens so viele Fahrzeuge eines jeweiligen Produktes produziert werden, sodass die Nachfrage des jeweiligen Produktes befriedigt ist.
constraint forall(p in Products)(soldCars[p] >= (demand_per_Product[p]));


%%%%%%%%%%%%__________________________Emission WLTP_______________________%%%%%%%%%%%%%%
%Berechnung der Summe der verkauften Fahrzeuge inklusive der Supercredit- Faktoren
constraint carsforWLTP_supercredit = sum(s in Sites, p in Products)(produce[s,p] * supercredit[p]);
%Berechnung des Gesamtgewichtes der verkauften Fahrzeugflotte
totalweight = (sum(s in Sites, p in Products)(produce[s,p] * weight[p]));
%Berechnung des durchschnittlichen Gewichtes der gesamten Fahrzeugflotte
constraint avgweight * sold = totalweight;
%Berechnung der Emissionsgrenze, welche durch den Automobilhersteller
%nicht überschritten werden darf, ohne Strafzahlungen leisten zu müssen.
emissionlimit = (payperfine + (0.0333 * (avgweight - 1380)));
%Berechnung der durch den Fahrzeughersteller gesamt-emittierten Emissionen.
emission = sum(s in Sites,p in Products)(produce[s,p] * supercredit[p] * (emissionWLTP[p]));
%Berechnung des durchschnittlichen WLTP-Wertes der gesamten Fahrzeugflotte.
constraint wltpavg * carsforWLTP_supercredit = emission;


%%%%%%%%___________KontrollbedingungenfürdieVariablenproduceunddelivered___________%%%%%%  
%Berechnung der insgesamt produzierten Produkte p
constraint sold = sum(s in Sites, p in Products)(produce[s,p]);
%Berechnung der insgesamt ausgelieferten Produkte p
constraint delivered_total = sum(s in Sites, c in Customers,  p in Products)(delivered[s,c, p]);
%Es werden ebenso viele Fahrzeuge produziert wie auch ausgeliefert werden
constraint sold == delivered_total;

%Kann vernachlässigt werden
constraint forall (p in Products) (     
      emissionPerCar[p] = (sum(s in Sites)(((produce[s,p]) * (emissionWLTP[p] - 97))))
);  


%Berechnung der individuellen Strafzahlungen des Automobilherstellers
constraint emissionRealFine = wltpdif * sold * payperfine;

%Berechnung der Profite des Automobilherstellers (gegliedert nach
%Gesamtprofit/ Produktprofit/ Kundenprofit)
constraint totalSales = sum (s in Sites, c in Customers, p in Products) (eb[c, p] * delivered[s,c,p]);

constraint forall(p in Products) (totalSales_perProduct[p] = (sum (s in Sites, c in Customers) (eb[c, p] * delivered[s,c,p])));

constraint forall(c in Customers) (totalSales_perCustomer[c] = (sum (s in Sites, p in Products) (eb[c, p] * delivered[s,c,p])));

%Die Zielfunktion maximiert die Differenz zwischen dem Gesamtprofit und der Strafzahlungen des Automobilherstellers.
constraint total = totalSales - emissionRealFine;
solve maximize total;
