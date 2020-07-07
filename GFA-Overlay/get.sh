#!/bin/sh

log1() { echo "===> $1"; }
log2() { echo " ==> $1"; }
log3() { echo "  => $1"; }

apk add curl

log1 "Downloading GFA ..."
log2 "Region 33 ..."

#wget -q -O gfa-33.html 'https://flightplanning.navcanada.ca/cgi-bin/GenerProduit.pl?Produit=GFA&Region=33&Langue=anglais&NoSession=NS_Inconnu&Mode=graph'
#wget -q 'https://flightplanning.navcanada.ca/Latest/gfa/anglais/Latest-gfacn33_cldwx_000-e.html'

wget -q 'https://flightplanning.navcanada.ca/Latest/gfa/anglais/produits/uprair/gfa/gfacn33/Latest-gfacn33_cldwx_000.png'
