# ==========================================
# ADVANCED SWING TRADING SYSTEM + WEBULL OPENAPI EXECUTION
# ==========================================
#
# NOTES BEFORE YOU RUN THIS:
#
# 1. This uses Webull's OFFICIAL OpenAPI / SDK
#    (pip3 install --upgrade webull-openapi-python-sdk).
#    Set your credentials as environment variables:
#        $env:WEBULL_APP_KEY="your_key"
#        $env:WEBULL_APP_SECRET="your_secret"
#
# 2. The script filters scan results using these rules:
#       - Signal == BUY
#       - Target >= Entry * 1.15  (>=15% upside to target)
#       - Win Rate between 80 and 100
#       - Backtest Return (R) >= 5
#    Then takes the top 7 by Win Rate / Backtest Return.
#
# 3. Before ANY order is sent, the script prints the current
#    portfolio, shows you the candidate trade, and asks you
#    to confirm order type + dollar amount for THAT trade.
#    Nothing is bought automatically without your input.
#
# 4. Selling is intentionally NOT implemented.
#
# 5. This is not financial advice.
#
# ==========================================
# ==========================================
# ADVANCED SWING TRADING SYSTEM


import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use("TkAgg")  # opens charts in a separate window
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import math
import os
import uuid

from webull.core.client import ApiClient
from webull.trade.trade_client import TradeClient

# ==========================================
# STOCK LIST
# ==========================================

stocks = [
    "AACB", "AACBR", "AACBU", "AACG", "AACI", "AACIU", "AACIW", "AACO", "AACOU", "AACOW",
    "AACP", "AACPR", "AACPU", "AACPW", "AADR", "AAEQ", "AAL", "AALG", "AAME", "AAOI",
    "AAON", "AAPB", "AAPD", "AAPG", "AAPL", "AAPU", "AARD", "AAUS", "AAVM", "AAXJ",
    "ABAT", "ABCL", "ABCS", "ABEO", "ABI", "ABIG", "ABLV", "ABLVW", "ABNB", "ABNG",
    "ABOS", "ABSI", "ABTC", "ABTS", "ABUS", "ABVC", "ABVX", "ACAA", "ACAAU", "ACAAW",
    "ACAD", "ACB", "ACCL", "ACDC", "ACEP", "ACET", "ACFN", "ACGC", "ACGCU", "ACGCW",
    "ACGL", "ACGLN", "ACGLO", "ACHC", "ACHV", "ACIC", "ACIU", "ACIW", "ACLS", "ACMR",
    "ACNB", "ACNT", "ACOG", "ACON", "ACONW", "ACRS", "ACRV", "ACT", "ACTG", "ACTU",
    "ACWI", "ACWX", "ACXP", "ADAC", "ADACU", "ADACW", "ADAG", "ADAM", "ADAMG", "ADAMH",
    "ADAMI", "ADAML", "ADAMM", "ADAMN", "ADAMO", "ADAMZ", "ADBE", "ADBG", "ADEA", "ADGM",
    "ADI", "ADIL", "ADMA", "ADP", "ADPT", "ADSE", "ADSEW", "ADSK", "ADTN", "ADTX",
    "ADUR", "ADUS", "ADV", "ADVB", "ADXN", "AEAQ", "AEAQU", "AEAQW", "AEBI", "AEC",
    "AEHL", "AEHR", "AEI", "AEIS", "AEMD", "AENT", "AENTW", "AEP", "AERT", "AERTW",
    "AESPU", "AEVA", "AEYE", "AFBI", "AFCG", "AFJK", "AFJKR", "AFJKU", "AFOS", "AFRI",
    "AFRIW", "AFRM", "AFSC", "AFYA", "AGCC", "AGEM", "AGEN", "AGGA", "AGIO", "AGIX",
    "AGMB", "AGMH", "AGMI", "AGNC", "AGNCL", "AGNCM", "AGNCN", "AGNCO", "AGNCP", "AGNCZ",
    "AGNG", "AGNT", "AGPU", "AGRZ", "AGYS", "AGZD", "AHCO", "AHD", "AHG", "AHMA",
    "AIA", "AIAI", "AIDX", "AIFA", "AIFC", "AIFD", "AIFF", "AIFU", "AIHS", "AIIO",
    "AIIOW", "AIIR", "AIMD", "AIMDW", "AIMS", "AIOS", "AIOT", "AIP", "AIPI", "AIPO",
    "AIQ", "AIRE", "AIRG", "AIRJ", "AIRJW", "AIRO", "AIRR", "AIRS", "AIRT", "AIRTP",
    "AISP", "AISPW", "AIXC", "AIXI", "AKAM", "AKAN", "AKBA", "AKTS", "AKTX", "ALAB",
    "ALAR", "ALBG", "ALBT", "ALCO", "ALDF", "ALDFU", "ALDFW", "ALDX", "ALEC", "ALF",
    "ALFUU", "ALFUW", "ALGM", "ALGN", "ALGS", "ALGT", "ALHC", "ALIL", "ALIS", "ALISR",
    "ALISU", "ALKS", "ALKT", "ALLO", "ALLR", "ALLT", "ALLW", "ALM", "ALMR", "ALMS",
    "ALMU", "ALNT", "ALNY", "ALOT", "ALOV", "ALOVU", "ALOVW", "ALOY", "ALP", "ALPS",
    "ALRM", "ALRS", "ALT", "ALTI", "ALTO", "ALTY", "ALVO", "ALVOW", "ALXO", "ALZN",
    "AMA", "AMAL", "AMAN", "AMAT", "AMBA", "AMBR", "AMCI", "AMCX", "AMD", "AMDD",
    "AMDG", "AMDL", "AMGN", "AMID", "AMIX", "AMKR", "AMLX", "AMOD", "AMODW", "AMPG",
    "AMPGR", "AMPGZ", "AMPH", "AMPL", "AMRN", "AMRX", "AMSC", "AMSF", "AMSS", "AMST",
    "AMTX", "AMUN", "AMUU", "AMYY", "AMZD", "AMZN", "AMZU", "AMZZ", "ANAB", "ANDE",
    "ANEL", "ANGH", "ANGHW", "ANGI", "ANGL", "ANGO", "ANIK", "ANIP", "ANIX", "ANL",
    "ANNA", "ANNAW", "ANNX", "ANPA", "ANSC", "ANSCU", "ANSCW", "ANTA", "ANTX", "ANV",
    "ANY", "AOHY", "AOSL", "AOTG", "AOUT", "APA", "APAC", "APACR", "APACU", "APC",
    "APEI", "APGE", "API", "APLD", "APLM", "APLMW", "APM", "APMCU", "APOG", "APP",
    "APPF", "APPN", "APPS", "APPX", "APRE", "APURU", "APVO", "APWC", "APXT", "APXTU",
    "APXTW", "APYX", "AQB", "AQLG", "AQMS", "AQST", "AQWA", "ARAI", "ARAY", "ARBB",
    "ARBE", "ARBEW", "ARBK", "ARCB", "ARCC", "ARCI", "ARCIU", "ARCIW", "ARCL", "ARCLR",
    "ARCLU", "ARCLW", "ARCT", "ARDX", "AREC", "ARGX", "ARHS", "ARKO", "ARKR", "ARLP",
    "ARM", "ARMG", "ARMY", "AROW", "ARQ", "ARQQ", "ARQQW", "ARQT", "ARRY", "ARTC",
    "ARTCU", "ARTCW", "ARTL", "ARTNA", "ARTV", "ARTW", "ARVN", "ARVR", "ARWR", "ARXS",
    "ASBP", "ASBPW", "ASCI", "ASD", "ASEC", "ASLE", "ASMB", "ASMG", "ASML", "ASMU",
    "ASND", "ASO", "ASPC", "ASPCR", "ASPCU", "ASPI", "ASPS", "ASPSW", "ASPSZ", "ASRT",
    "ASRV", "ASST", "ASTC", "ASTE", "ASTH", "ASTI", "ASTL", "ASTLW", "ASTS", "ASUR",
    "ASYS", "ATAI", "ATAT", "ATC", "ATCX", "ATEC", "ATER", "ATEX", "ATGL", "ATHE",
    "ATHR", "ATII", "ATIIU", "ATIIW", "ATLC", "ATLCL", "ATLCP", "ATLCZ", "ATLN", "ATLO",
    "ATLX", "ATNI", "ATOM", "ATOS", "ATPC", "ATRA", "ATRC", "ATRO", "ATXG", "ATYR",
    "AUBN", "AUC", "AUDC", "AUGO", "AUID", "AUMI", "AUPH", "AUR", "AURA", "AURE",
    "AUROW", "AUTL", "AUUD", "AVAH", "AVAV", "AVBH", "AVBP", "AVGB", "AVGG", "AVGO",
    "AVGU", "AVGX", "AVIR", "AVL", "AVLN", "AVNW", "AVO", "AVOS", "AVPT", "AVR",
    "AVS", "AVT", "AVTX", "AVUQ", "AVX", "AVXC", "AVXL", "AVXX", "AWRE", "AXG",
    "AXGN", "AXIN", "AXINR", "AXINU", "AXON", "AXPG", "AXSM", "AXTI", "AYA", "AYTU",
    "AZ", "AZI", "AZTA", "AZYY", "BABU", "BABX", "BACC", "BACCR", "BACCU", "BAER",
    "BAERW", "BAFE", "BAFN", "BAIG", "BAIV", "BALQ", "BAND", "BANF", "BANFP", "BANL",
    "BANR", "BANX", "BAOS", "BASG", "BASV", "BATRA", "BATRK", "BAYA", "BAYAR", "BAYAU",
    "BBB", "BBCP", "BBCQ", "BBCQU", "BBCQW", "BBGI", "BBH", "BBIO", "BBLG", "BBLGW",
    "BBNX", "BBOT", "BBSI", "BBYY", "BCAB", "BCAL", "BCAR", "BCARU", "BCARW", "BCAX",
    "BCBP", "BCDA", "BCFN", "BCG", "BCGWW", "BCIC", "BCLO", "BCML", "BCPC", "BCRX",
    "BCTK", "BCTX", "BCTXL", "BCTXZ", "BCYC", "BDCI", "BDCIU", "BDCIW", "BDGS", "BDMD",
    "BDMDW", "BDRX", "BDSX", "BDTX", "BDVL", "BDYN", "BEAG", "BEAGR", "BEAGU", "BEAM",
    "BEAT", "BEATW", "BEDY", "BEEM", "BEEP", "BEEX", "BEEZ", "BEG", "BELFA", "BELFB",
    "BELT", "BENF", "BENFW", "BESO", "BETR", "BETRW", "BFC", "BFLX", "BFRG", "BFRGW",
    "BFRI", "BFRIW", "BFST", "BGC", "BGCG", "BGDE", "BGEG", "BGGG", "BGIA", "BGIN",
    "BGL", "BGLC", "BGLWW", "BGM", "BGMS", "BGRN", "BGRO", "BHAV", "BHAVR", "BHAVU",
    "BHDG", "BHF", "BHFAL", "BHFAM", "BHFAN", "BHFAO", "BHFAP", "BHRB", "BHST", "BIAF",
    "BIAFW", "BIB", "BIDG", "BIDU", "BIDWU", "BIIB", "BILI", "BIOA", "BIOX", "BIOY",
    "BIRD", "BIS", "BITS", "BIVI", "BIVIW", "BIXI", "BIXIU", "BIXIW", "BIYA", "BJDX",
    "BJRI", "BKCH", "BKHA", "BKHAR", "BKHAU", "BKMI", "BKMS", "BKNG", "BKR", "BL",
    "BLBD", "BLCN", "BLCR", "BLDP", "BLFS", "BLIN", "BLIV", "BLKB", "BLLN", "BLMN",
    "BLNE", "BLNK", "BLRK", "BLRKU", "BLRKW", "BLRX", "BLSG", "BLTE", "BLUW", "BLUWU",
    "BLUWW", "BLZE", "BLZR", "BLZRU", "BLZRW", "BMBL", "BMEA", "BMGL", "BMHL", "BMM",
    "BMNG", "BMOP", "BMR", "BMRA", "BMRC", "BMRN", "BNAI", "BNAIW", "BNBX", "BNC",
    "BNCWW", "BNCWZ", "BND", "BNDP", "BNDW", "BNDX", "BNGO", "BNKK", "BNR", "BNRG",
    "BNTC", "BNTX", "BNZI", "BNZIW", "BODI", "BOEG", "BOEU", "BOF", "BOKF", "BOLD",
    "BOLT", "BON", "BOOM", "BOSC", "BOT", "BOTJ", "BOTT", "BOTZ", "BOXL", "BPAC",
    "BPACR", "BPACU", "BPOP", "BPOPM", "BPRN", "BPYPM", "BPYPN", "BPYPO", "BPYPP", "BRAG",
    "BRAI", "BRBI", "BRCB", "BREM", "BRES", "BREZU", "BRFH", "BRHY", "BRID", "BRKHU",
    "BRKR", "BRKRP", "BRKU", "BRLS", "BRLSW", "BRLT", "BRNS", "BRNY", "BRR", "BRRR",
    "BRRWW", "BRTR", "BRTX", "BRUN", "BRUNW", "BRZE", "BSAA", "BSAAR", "BSAAU", "BSBK",
    "BSCQ", "BSCR", "BSCS", "BSCT", "BSCU", "BSCV", "BSCW", "BSCX", "BSCY", "BSCZ",
    "BSET", "BSIN", "BSJQ", "BSJR", "BSJS", "BSJT", "BSJU", "BSJV", "BSJW", "BSJX",
    "BSMQ", "BSMR", "BSMS", "BSMT", "BSMU", "BSMV", "BSMW", "BSMY", "BSMZ", "BSRR",
    "BSSX", "BSVN", "BSVO", "BSY", "BTAI", "BTBD", "BTBDW", "BTBT", "BTCS", "BTCT",
    "BTDR", "BTF", "BTGD", "BTMD", "BTOC", "BTOG", "BTQ", "BTSG", "BTSGU", "BTTC",
    "BU", "BUFC", "BUFI", "BUFM", "BUG", "BULD", "BULG", "BULL", "BULLW", "BULX",
    "BUSE", "BUSEP", "BUUU", "BVC", "BVFL", "BVS", "BWAY", "BWB", "BWBBP", "BWEN",
    "BWFG", "BWIN", "BWMN", "BYAH", "BYFC", "BYND", "BYRN", "BYSI", "BZ", "BZAI",
    "BZAIW", "BZFD", "BZFDW", "BZUN", "CAAS", "CABA", "CABR", "CAC", "CACC", "CADL",
    "CAFG", "CAI", "CAIIU", "CAIQ", "CAKE", "CALC", "CALI", "CALM", "CAMP", "CAMT",
    "CAN", "CANC", "CANQ", "CAPN", "CAPNR", "CAPNU", "CAPR", "CAPS", "CAQ", "CAQUU",
    "CAQUW", "CAR", "CARE", "CARG", "CARL", "CART", "CARY", "CARZ", "CASH", "CASS",
    "CAST", "CASY", "CATH", "CATY", "CBAT", "CBC", "CBFV", "CBIO", "CBK", "CBLL",
    "CBNK", "CBRL", "CBRS", "CBSH", "CBUS", "CCAP", "CCAQ", "CCAQU", "CCAQW", "CCB",
    "CCBG", "CCC", "CCCC", "CCD", "CCEC", "CCEP", "CCFE", "CCG", "CCGWW", "CCHH",
    "CCII", "CCIIU", "CCIIW", "CCIX", "CCIXU", "CCIXW", "CCLD", "CCNE", "CCNEP", "CCNR",
    "CCOI", "CCRN", "CCSB", "CCSI", "CCSO", "CCTG", "CCXI", "CCXIU", "CCXIW", "CD",
    "CDC", "CDIG", "CDIO", "CDIOW", "CDL", "CDLX", "CDNA", "CDNL", "CDNS", "CDRO",
    "CDROW", "CDT", "CDTG", "CDTTW", "CDW", "CDXS", "CDZI", "CDZIP", "CECO", "CEFA",
    "CEG", "CELC", "CELH", "CELU", "CELUW", "CELZ", "CENN", "CENT", "CENTA", "CENX",
    "CEPF", "CEPI", "CEPO", "CEPS", "CEPT", "CEPV", "CERS", "CERT", "CETX", "CETY",
    "CEVA", "CFA", "CFBK", "CFFI", "CFFN", "CFO", "CG", "CGABL", "CGBD", "CGC",
    "CGEM", "CGEN", "CGNT", "CGNX", "CGO", "CGON", "CGTL", "CGTX", "CHA", "CHAI",
    "CHAR", "CHARR", "CHARU", "CHCI", "CHCO", "CHDN", "CHEC", "CHECU", "CHECW", "CHEF",
    "CHGX", "CHI", "CHKP", "CHMG", "CHNR", "CHPG", "CHPGR", "CHPGU", "CHPS", "CHPX",
    "CHR", "CHRD", "CHRI", "CHRN", "CHRS", "CHRW", "CHSCL", "CHSCM", "CHSCN", "CHSCO",
    "CHSCP", "CHSN", "CHTR", "CHW", "CHY", "CHYM", "CIBR", "CIFG", "CIFR", "CIGI",
    "CIIT", "CINF", "CING", "CINGW", "CISO", "CISS", "CIVB", "CJMB", "CLAR", "CLBK",
    "CLBT", "CLDX", "CLFD", "CLGN", "CLIK", "CLIR", "CLLS", "CLMB", "CLMT", "CLNE",
    "CLNN", "CLOA", "CLOD", "CLOU", "CLOV", "CLPS", "CLPT", "CLRB", "CLRO", "CLSK",
    "CLSKW", "CLSM", "CLST", "CLWT", "CLYM", "CMBO", "CMCO", "CMCSA", "CMCT", "CME",
    "CMGG", "CMII", "CMIIU", "CMIIW", "CMMB", "CMND", "CMPR", "CMPS", "CMPX", "CMRC",
    "CMTL", "CMTV", "CNCG", "CNCK", "CNCKW", "CNDT", "CNET", "CNEY", "CNOB", "CNOBP",
    "CNQQ", "CNSP", "CNTA", "CNTB", "CNTN", "CNTX", "CNTY", "CNVS", "CNXC", "CNXN",
    "CNXU", "COAG", "COCH", "COCHW", "COCO", "COCP", "CODA", "CODX", "COFS", "COGT",
    "COHU", "COIG", "COIN", "COKE", "COLA", "COLAR", "COLAU", "COLB", "COLL", "COLM",
    "COMT", "CONI", "CONL", "CONX", "COO", "COOT", "COOTW", "COPJ", "COPP", "CORO",
    "CORT", "CORZ", "CORZW", "CORZZ", "COSM", "COST", "COTG", "COWG", "COWS", "COYA",
    "COYY", "CPAG", "CPB", "CPBI", "CPHC", "CPHY", "CPIX", "CPLS", "CPOP", "CPRT",
    "CPRX", "CPSH", "CPSS", "CPZ", "CRAC", "CRACR", "CRACU", "CRACW", "CRAI", "CRAN",
    "CRANR", "CRANU", "CRAQ", "CRAQR", "CRAQU", "CRBP", "CRBU", "CRCG", "CRCT", "CRDF",
    "CRDL", "CRDO", "CRE", "CREG", "CRESY", "CREX", "CRGO", "CRGOW", "CRIS", "CRMD",
    "CRMG", "CRML", "CRMLW", "CRMT", "CRMU", "CRNC", "CRNT", "CRNX", "CRON", "CROX",
    "CRSP", "CRSR", "CRTO", "CRUS", "CRVL", "CRVO", "CRVS", "CRWD", "CRWG", "CRWL",
    "CRWS", "CRWV", "CRY", "CSAI", "CSB", "CSBR", "CSCL", "CSCO", "CSCS", "CSGP",
    "CSHR", "CSHRW", "CSIQ", "CSPI", "CSQ", "CSTE", "CSTL", "CSWC", "CSX", "CTAA",
    "CTAAR", "CTAAU", "CTAS", "CTBI", "CTEC", "CTKB", "CTMX", "CTNM", "CTNT", "CTOR",
    "CTRM", "CTRN", "CTSH", "CTSO", "CTW", "CTXR", "CUB", "CUBWU", "CUBWW", "CUE",
    "CULP", "CUPR", "CURI", "CURR", "CURX", "CUSD", "CV", "CVBF", "CVCO", "CVGI",
    "CVKD", "CVLT", "CVNX", "CVRX", "CVV", "CWBC", "CWCO", "CWD", "CWST", "CWY",
    "CXAI", "CXAIW", "CXDO", "CXIIU", "CXSE", "CYAB", "CYCN", "CYCU", "CYCUW", "CYN",
    "CYPH", "CYRX", "CYTK", "CZAR", "CZFS", "CZNC", "CZR", "CZWI", "DAAQ", "DAAQU",
    "DAAQW", "DADS", "DAIC", "DAICW", "DAIO", "DAK", "DAKT", "DALI", "DAPP", "DARE",
    "DASH", "DAVE", "DAVEW", "DAX", "DBCA", "DBCAU", "DBCAW", "DBGI", "DBVT", "DBX",
    "DCBO", "DCGO", "DCOY", "DCTH", "DCX", "DDI", "DDIV", "DDOG", "DECO", "DEFT",
    "DEMZ", "DERM", "DETX", "DEVS", "DFDV", "DFDVW", "DFGP", "DFGX", "DFLI", "DFLIW",
    "DFNS", "DFNSW", "DFSC", "DFSCW", "DFTX", "DGCB", "DGICA", "DGICB", "DGII", "DGLO",
    "DGNX", "DGRE", "DGRS", "DGRW", "DGXX", "DH", "DHC", "DHCNI", "DHCNL", "DIBS",
    "DIME", "DINE", "DIOD", "DIVD", "DJCO", "DJT", "DJTWW", "DKI", "DKNG", "DKNX",
    "DLHC", "DLLL", "DLO", "DLPN", "DLTH", "DLTR", "DLXY", "DMAA", "DMAAR", "DMAAU",
    "DMAC", "DMII", "DMIIR", "DMIIU", "DMLP", "DMRA", "DMRC", "DMXF", "DNLI", "DNMX",
    "DNMXU", "DNMXW", "DNNG", "DNTH", "DNUT", "DOCU", "DOGZ", "DOMH", "DOMO", "DOO",
    "DORM", "DOX", "DOYU", "DPRO", "DPZ", "DRCT", "DRDB", "DRDBU", "DRDBW", "DRH",
    "DRIO", "DRIV", "DRMA", "DRMAW", "DRNZ", "DRS", "DRTS", "DRTSW", "DRUG", "DRVN",
    "DSAC", "DSACU", "DSACW", "DSGN", "DSGR", "DSGX", "DSP", "DSWL", "DSY", "DSYWW",
    "DTCR", "DTCX", "DTI", "DTIL", "DTSQ", "DTSQR", "DTSQU", "DTSS", "DTST", "DUKH",
    "DUKR", "DUKRW", "DUKX", "DUO", "DUOG", "DUOL", "DUOT", "DUSG", "DVAL", "DVGR",
    "DVIN", "DVLT", "DVLU", "DVOL", "DVQQ", "DVRE", "DVSP", "DVUT", "DVXB", "DVXC",
    "DVXE", "DVXF", "DVXK", "DVXP", "DVXV", "DVXY", "DVY", "DWAS", "DWAW", "DWSH",
    "DWSN", "DWTX", "DWUS", "DXCM", "DXLG", "DXPE", "DXR", "DXST", "DYAI", "DYFI",
    "DYN", "DYNB", "DYNC", "DYNCU", "DYNCW", "DYOR", "DYORU", "DYORW", "DYTA", "EA",
    "EART", "EASY", "EBAY", "EBC", "EBI", "EBIZ", "EBMT", "EBON", "ECBK", "ECOR",
    "ECOW", "ECPG", "ECX", "ECXWW", "EDBL", "EDBLW", "EDHL", "EDIT", "EDRY", "EDSA",
    "EDTK", "EDUC", "EEE", "EEFT", "EEIQ", "EEMA", "EFAS", "EFOI", "EFRA", "EFSC",
    "EFSCP", "EFSI", "EFTY", "EGAN", "EGBN", "EGGQ", "EGHA", "EGHAR", "EGHAU", "EGHT",
    "EH", "EHGO", "EHLD", "EHLS", "EHTH", "EIKN", "EJH", "EKG", "ELAB", "ELBM",
    "ELDN", "ELE", "ELFY", "ELIL", "ELMT", "ELOG", "ELPW", "ELSE", "ELTK", "ELTX",
    "ELUT", "ELVA", "ELVN", "ELVR", "ELWT", "EMAT", "EMB", "EMBC", "EMCB", "EMEM",
    "EMEQ", "EMIF", "EMIS", "EMISR", "EML", "EMPD", "EMPG", "EMSC", "EMXC", "EMXF",
    "ENDW", "ENGN", "ENGNW", "ENGS", "ENHI", "ENHU", "ENLT", "ENLV", "ENPH", "ENSC",
    "ENSG", "ENTA", "ENTG", "ENTX", "ENVB", "ENVX", "ENZL", "EOLS", "EOSE", "EPOW",
    "EPRX", "EPSM", "EPSN", "EQ", "EQIX", "EQPT", "EQRR", "ERAS", "ERET", "ERIC",
    "ERIE", "ERII", "ERNA", "ERNAW", "ESCA", "ESEA", "ESGD", "ESGE", "ESGU", "ESLA",
    "ESLAW", "ESLT", "ESMV", "ESN", "ESOA", "ESPO", "ESPR", "ESQ", "ESTA", "ETEC",
    "ETHA", "ETHB", "ETON", "ETOR", "ETRL", "ETS", "EU", "EUDA", "EUDAW", "EUFN",
    "EURK", "EURKR", "EURKU", "EVAX", "EVCM", "EVER", "EVGN", "EVGO", "EVGOW", "EVLV",
    "EVLVW", "EVMT", "EVO", "EVOX", "EVOXU", "EVOXW", "EVPF", "EVRG", "EVSD", "EVTV",
    "EVYM", "EWBC", "EWJV", "EWTX", "EWZS", "EXC", "EXE", "EXEL", "EXFY", "EXLS",
    "EXOZ", "EXPE", "EXPO", "EXTR", "EXUS", "EXYN", "EXYNW", "EYE", "EYEG", "EYPT",
    "EZGO", "EZMO", "EZPW", "EZRA", "EZRO", "FA", "FAAA", "FAAR", "FAB", "FABC",
    "FAC", "FACT", "FACTU", "FACTW", "FACWW", "FAD", "FALN", "FAMI", "FANG", "FAST",
    "FATE", "FATN", "FBGL", "FBIO", "FBIOP", "FBIZ", "FBL", "FBLA", "FBLG", "FBNC",
    "FBOT", "FBRX", "FBYD", "FBYDP", "FBYDW", "FBYY", "FCA", "FCAL", "FCAP", "FCBC",
    "FCCO", "FCEF", "FCEL", "FCFS", "FCHL", "FCLO", "FCNCA", "FCNCN", "FCNCO", "FCNCP",
    "FCTE", "FCUV", "FCVT", "FCXG", "FDBC", "FDCF", "FDFF", "FDIF", "FDIG", "FDIQ",
    "FDIV", "FDMT", "FDNI", "FDRS", "FDRX", "FDSB", "FDT", "FDTS", "FDTX", "FDUS",
    "FEAM", "FEAT", "FEBO", "FEED", "FEIM", "FELE", "FEM", "FEMB", "FEMS", "FEMY",
    "FENC", "FEP", "FEPI", "FER", "FERA", "FERAR", "FERAU", "FEUZ", "FEX", "FFAI",
    "FFAIW", "FFBC", "FFIN", "FFIV", "FFUT", "FGBI", "FGBIP", "FGI", "FGII", "FGIIU",
    "FGIIW", "FGIWW", "FGL", "FGM", "FGMC", "FGMCR", "FGMCU", "FGNX", "FGNXP", "FGSI",
    "FHB", "FHTX", "FIBK", "FICS", "FID", "FIEE", "FIGG", "FIGR", "FIGX", "FIGXU",
    "FIGXW", "FINW", "FINX", "FINY", "FIP", "FISI", "FISV", "FITB", "FITBI", "FITBM",
    "FITBO", "FITBP", "FIVE", "FIVN", "FIVY", "FIXD", "FIYY", "FIZZ", "FJP", "FKU",
    "FKWL", "FLD", "FLDB", "FLDDW", "FLEX", "FLGT", "FLL", "FLN", "FLNA", "FLNC",
    "FLNT", "FLUX", "FLWS", "FLX", "FLXS", "FLY", "FLYE", "FLYW", "FMAC", "FMACR",
    "FMACU", "FMAO", "FMB", "FMBH", "FMED", "FMET", "FMFC", "FMHI", "FMNB", "FMST",
    "FMSTW", "FMTM", "FMUB", "FMUN", "FNGR", "FNK", "FNKO", "FNLC", "FNRN", "FNUC",
    "FNWB", "FNWD", "FNX", "FNY", "FOCL", "FOFO", "FORM", "FORR", "FORTY", "FOSL",
    "FOX", "FOXA", "FOXF", "FOXX", "FOXXW", "FPA", "FPXE", "FPXI", "FRAF", "FRBA",
    "FRD", "FRGT", "FRHC", "FRME", "FRMEP", "FRMI", "FRMM", "FROG", "FRPH", "FRPT",
    "FRSH", "FRST", "FRSX", "FRTT", "FRVO", "FRWD", "FSBC", "FSBW", "FSCS", "FSEA",
    "FSGS", "FSHP", "FSHPR", "FSHPU", "FSLR", "FSLY", "FSTR", "FSUN", "FSV", "FSZ",
    "FTA", "FTAG", "FTAI", "FTAIM", "FTAIN", "FTC", "FTCI", "FTCS", "FTDR", "FTDS",
    "FTEK", "FTFT", "FTGC", "FTGS", "FTHAU", "FTHI", "FTHM", "FTLF", "FTNT", "FTQI",
    "FTRE", "FTRI", "FTRK", "FTSL", "FTSM", "FTXG", "FTXH", "FTXL", "FTXN", "FTXO",
    "FTXR", "FUFU", "FUFUW", "FULC", "FULT", "FULTP", "FUNC", "FUND", "FUSB", "FUSE",
    "FUSEW", "FUTG", "FUTU", "FV", "FVAV", "FVC", "FVCB", "FVN", "FVNNR", "FVNNU",
    "FWDI", "FWONA", "FWONK", "FWRD", "FWRG", "FXACU", "FXNC", "FYC", "FYT", "FYX",
    "GABC", "GAIA", "GAIN", "GAING", "GAINI", "GAINZ", "GALT", "GAMB", "GAME", "GANX",
    "GARY", "GASS", "GAUZ", "GAVA", "GBDC", "GBFH", "GBLI", "GBUG", "GCBC", "GCGRU",
    "GCL", "GCLWW", "GCMG", "GCT", "GCTK", "GDC", "GDEV", "GDEVW", "GDHG", "GDRX",
    "GDS", "GDTC", "GDYN", "GECC", "GECCG", "GECCH", "GECCI", "GEG", "GEGGL", "GEHC",
    "GELS", "GEME", "GEMG", "GEMI", "GEN", "GENB", "GENK", "GENVR", "GENZ", "GEOS",
    "GERN", "GEVG", "GEVO", "GEW", "GFAI", "GFAIW", "GFGF", "GFLW", "GFS", "GGAL",
    "GGLL", "GGLS", "GGR", "GGROW", "GGRP", "GH", "GHRS", "GIBO", "GIBOW", "GIEQ",
    "GIFT", "GIGM", "GIII", "GILD", "GILT", "GIND", "GINX", "GIPR", "GIPRW", "GITS",
    "GIW", "GIWWR", "GIWWU", "GIX", "GIXXR", "GIXXU", "GKAT", "GLAD", "GLBE", "GLBS",
    "GLCR", "GLDB", "GLDI", "GLDY", "GLE", "GLGG", "GLIBA", "GLIBK", "GLMD", "GLND",
    "GLNDW", "GLNG", "GLOO", "GLOW", "GLPI", "GLRE", "GLSI", "GLUE", "GLWG", "GLXG",
    "GLXY", "GMAB", "GMEX", "GMHS", "GMM", "GNLN", "GNLX", "GNMA", "GNOM", "GNPX",
    "GNSS", "GNTA", "GNTX", "GO", "GOAI", "GOCO", "GOGO", "GOOD", "GOODN", "GOODO",
    "GOOG", "GOOGL", "GOOGM", "GOOGN", "GOSS", "GOU", "GOVI", "GOVX", "GP", "GPAC",
    "GPACU", "GPACW", "GPAT", "GPATU", "GPATW", "GPCR", "GPIQ", "GPIX", "GPRE", "GPRF",
    "GPRO", "GPT", "GQQQ", "GRAB", "GRABW", "GRAG", "GRAL", "GRAN", "GRCE", "GRDX",
    "GREE", "GREEL", "GRFS", "GRI", "GRID", "GRIN", "GRML", "GRMLW", "GRNQ", "GROW",
    "GRPN", "GRRR", "GRRRW", "GRVY", "GRW", "GRWG", "GSAT", "GSBC", "GSGO", "GSHD",
    "GSHR", "GSHRU", "GSHRW", "GSIB", "GSIT", "GSIW", "GSM", "GSRF", "GSRFR", "GSRFU",
    "GSRVU", "GSUN", "GT", "GTBP", "GTEC", "GTEN", "GTENU", "GTENW", "GTERA", "GTERR",
    "GTERU", "GTERW", "GTIM", "GTLB", "GTM", "GTOP", "GTOQ", "GTPE", "GTR", "GTX",
    "GUACU", "GURE", "GUSE", "GUTS", "GV", "GVH", "GVLE", "GWAV", "GWRS", "GXAI",
    "GXDW", "GYRE", "GYRO", "HACQ", "HACQU", "HACQW", "HAFC", "HAIN", "HALO", "HAO",
    "HAS", "HAVA", "HAVAR", "HAVAU", "HBAN", "HBANL", "HBANM", "HBANP", "HBANZ", "HBCP",
    "HBDC", "HBIO", "HBNB", "HBNC", "HBR", "HBT", "HCAC", "HCACR", "HCACU", "HCAI",
    "HCAT", "HCHL", "HCIC", "HCICR", "HCICU", "HCKT", "HCM", "HCMA", "HCMAU", "HCMAW",
    "HCOW", "HCSG", "HCTI", "HCWB", "HDL", "HDRN", "HDRNW", "HDSN", "HEAL", "HECO",
    "HELE", "HELP", "HEPS", "HEQQ", "HERD", "HERE", "HERO", "HERZ", "HFBL", "HFFG",
    "HFSP", "HFWA", "HGBL", "HHS", "HIDE", "HIFS", "HIHO", "HIMX", "HIMZ", "HIND",
    "HIS", "HISF", "HIT", "HITI", "HIVE", "HKIT", "HKPD", "HLAL", "HLIT", "HLMN",
    "HLNE", "HLP", "HLXC", "HMH", "HMR", "HMYY", "HNDL", "HNNA", "HNNAZ", "HNRG",
    "HNST", "HNVR", "HODU", "HOFT", "HOLO", "HOLOW", "HON", "HOOD", "HOOG", "HOOX",
    "HOPE", "HOUR", "HOVNP", "HOVR", "HOVRW", "HOWL", "HOYY", "HPAI", "HPAIW", "HPK",
    "HQ", "HQGO", "HQI", "HQWWW", "HQY", "HRMY", "HROW", "HRTS", "HRTX", "HRZN",
    "HSAI", "HSCS", "HSCSW", "HSDT", "HSIC", "HSPT", "HSPTR", "HSPTU", "HST", "HSTM",
    "HTCO", "HTCR", "HTFL", "HTHT", "HTLD", "HTLM", "HTO", "HTOO", "HTZ", "HTZWW",
    "HUBC", "HUBCW", "HUBCZ", "HUBG", "HUDI", "HUHU", "HUIZ", "HUMA", "HUMAW", "HURA",
    "HURC", "HURN", "HUT", "HUTG", "HVII", "HVIIR", "HVIIU", "HVMC", "HVMCU", "HVMCW",
    "HWAY", "HWBK", "HWC", "HWCPZ", "HWH", "HWKN", "HWSM", "HXHX", "HYBI", "HYDR",
    "HYFM", "HYFT", "HYLS", "HYMC", "HYNE", "HYP", "HYPD", "HYPG", "HYPR", "HYXF",
    "HYZD", "IACO", "IACOU", "IACOW", "IACQU", "IALT", "IART", "IBAC", "IBACR", "IBAT",
    "IBB", "IBBQ", "IBCP", "IBEX", "IBG", "IBGA", "IBGB", "IBGC", "IBGK", "IBGL",
    "IBGM", "IBIO", "IBIT", "IBKR", "IBOC", "IBOT", "IBRX", "IBTG", "IBTH", "IBTI",
    "IBTJ", "IBTK", "IBTL", "IBTM", "IBTO", "IBTP", "IBTQ", "IBTR", "ICCC", "ICCM",
    "ICFI", "ICG", "ICHR", "ICLN", "ICLR", "ICMB", "ICON", "ICOP", "ICU", "ICUCW",
    "ICUI", "IDACU", "IDAI", "IDCC", "IDEF", "IDN", "IDVY", "IDXX", "IDYA", "IEAG",
    "IEAGR", "IEAGU", "IEF", "IEI", "IEP", "IESC", "IEUS", "IFBD", "IFGL", "IFLO",
    "IFRX", "IFV", "IGAC", "IGACR", "IGACU", "IGF", "IGIB", "IGIC", "IGOV", "IGSB",
    "IHRT", "III", "IIIV", "IJT", "IKT", "ILAG", "ILIT", "ILLR", "ILLRW", "ILLU",
    "ILLUU", "ILLUW", "ILMN", "ILPT", "IMA", "IMCC", "IMCR", "IMCV", "IMDX", "IMKTA",
    "IMMP", "IMMR", "IMMX", "IMNM", "IMNN", "IMOM", "IMOS", "IMPP", "IMPPP", "IMRN",
    "IMRX", "IMSR", "IMSRW", "IMTE", "IMTX", "IMUX", "IMVT", "IMXI", "INAB", "INAC",
    "INACR", "INACU", "INBK", "INBKZ", "INBS", "INBX", "INCR", "INCY", "IND", "INDB",
    "INDH", "INDI", "INDP", "INDQ", "INDV", "INDY", "INEO", "INGN", "INHD", "INIO",
    "INKT", "INLF", "INM", "INMB", "INMD", "INNV", "INO", "INOD", "INRO", "INSE",
    "INSG", "INSM", "INTA", "INTC", "INTG", "INTJ", "INTR", "INTS", "INTU", "INTW",
    "INTZ", "INV", "INVA", "INVE", "INVZ", "IONL", "IONR", "IONS", "IONX", "IONZ",
    "IOSP", "IOTR", "IOVA", "IOYY", "IPAR", "IPCX", "IPCXR", "IPCXU", "IPDN", "IPEX",
    "IPEXR", "IPEXU", "IPFX", "IPFXU", "IPFXW", "IPGP", "IPHA", "IPKW", "IPM", "IPSC",
    "IPST", "IPVVU", "IPW", "IPWR", "IPX", "IQ", "IQQQ", "IQST", "IRD", "IRDM",
    "IREG", "IREN", "IRHO", "IRHOR", "IRHOU", "IRIX", "IRMD", "IRON", "IRTC", "IRWD",
    "ISBA", "ISHG", "ISHP", "ISPC", "ISPR", "ISRG", "ISSC", "ISTB", "ISTM", "ISTR",
    "ISUL", "ITHA", "ITHAU", "ITHAW", "ITIC", "ITOC", "ITRI", "ITRN", "IUS", "IUSB",
    "IUSG", "IUSV", "IVA", "IVAL", "IVDA", "IVDAW", "IVF", "IVSI", "IVSS", "IVSX",
    "IVVD", "IXHL", "IXUS", "IZEA", "IZM", "JACK", "JAGX", "JAKK", "JANX", "JAPN",
    "JATT", "JAZZ", "JBDI", "JBHT", "JBIO", "JBLU", "JBSS", "JCAP", "JCSE", "JCTC",
    "JD", "JDOC", "JDZG", "JEM", "JEMA", "JEPQ", "JF", "JFB", "JFIN", "JFU",
    "JG", "JGLO", "JHAI", "JIVE", "JJSF", "JKHY", "JL", "JLHL", "JMID", "JMSB",
    "JOUT", "JOYT", "JOYY", "JPEF", "JPFP", "JPY", "JRSH", "JRVR", "JSM", "JSMD",
    "JSML", "JSPR", "JSPRW", "JTAI", "JTEK", "JUNS", "JVA", "JWEL", "JXG", "JYD",
    "JYNT", "JZ", "JZXN", "KALA", "KALU", "KALV", "KARO", "KAT", "KBAB", "KBDU",
    "KBON", "KBONU", "KBONW", "KBSX", "KBWB", "KBWD", "KBWP", "KBWY", "KC", "KCHV",
    "KCHVR", "KCHVU", "KDK", "KDKRW", "KDP", "KE", "KEAT", "KEEL", "KELYA", "KELYB",
    "KEQU", "KEYYU", "KFFB", "KFII", "KFIIR", "KFIIU", "KG", "KGEI", "KHC", "KIDS",
    "KIDZ", "KIDZW", "KINS", "KIQQ", "KITT", "KITTW", "KJD", "KLAC", "KLAG", "KLIC",
    "KLRA", "KLRS", "KLTR", "KLXE", "KMB", "KMDA", "KMLI", "KMRK", "KMTS", "KNDI",
    "KNGZ", "KNSA", "KOD", "KOID", "KOPN", "KOSS", "KOYN", "KOYNU", "KOYNW", "KPDD",
    "KPLT", "KPLTW", "KPRX", "KPTI", "KQQQ", "KRAQ", "KRAQU", "KRAQW", "KRKR", "KRMA",
    "KRMD", "KRNT", "KRNY", "KROP", "KROS", "KRRO", "KRT", "KRUS", "KRYS", "KSCP",
    "KSPI", "KTCC", "KTOS", "KTTA", "KTTAW", "KTWO", "KTWOR", "KTWOU", "KURA", "KUST",
    "KVAC", "KVACU", "KVACW", "KVHI", "KWM", "KWMWW", "KXIN", "KYIV", "KYIVW", "KYMR",
    "KYNB", "KYTX", "KZIA", "LAB", "LABT", "LACG", "LAES", "LAFA", "LAFAR", "LAFAU",
    "LAKE", "LAMR", "LAND", "LANDO", "LANDP", "LARK", "LASE", "LASR", "LATA", "LATAU",
    "LATAW", "LAUR", "LAWR", "LBGJ", "LBRDA", "LBRDK", "LBRDP", "LBRX", "LBTYA", "LBTYB",
    "LBTYK", "LCCC", "LCCCR", "LCCCU", "LCDL", "LCDS", "LCFY", "LCFYW", "LCID", "LCNB",
    "LCUT", "LDEM", "LDRX", "LDSF", "LE", "LECO", "LEDS", "LEE", "LEGH", "LEGN",
    "LEGR", "LEND", "LENZ", "LESL", "LEXI", "LEXX", "LFAC", "LFACU", "LFACW", "LFCR",
    "LFMD", "LFMDP", "LFS", "LFSC", "LFST", "LFTO", "LFUS", "LFVN", "LFWD", "LGCF",
    "LGCL", "LGHL", "LGIH", "LGN", "LGND", "LGO", "LGRO", "LGVN", "LHAI", "LHSW",
    "LI", "LICN", "LIDR", "LIDRW", "LIEN", "LIF", "LIFE", "LILA", "LILAK", "LILAV",
    "LILKV", "LILPV", "LIMN", "LIMNW", "LIN", "LINC", "LIND", "LINE", "LINK", "LINT",
    "LIQT", "LITE", "LITP", "LITS", "LIVE", "LIVN", "LIXT", "LKFN", "LKFT", "LKQ",
    "LKSP", "LKSPR", "LKSPU", "LLYVA", "LLYVK", "LMAT", "LMB", "LMBS", "LMFA", "LMNR",
    "LMNX", "LMRI", "LMTL", "LNAI", "LNKS", "LNSR", "LNT", "LNTH", "LNZA", "LNZAW",
    "LOAN", "LOBO", "LOCO", "LOGI", "LOGO", "LOKV", "LOKVU", "LOKVW", "LONA", "LOOP",
    "LOPE", "LOT", "LOTI", "LOTWW", "LOVE", "LPAA", "LPAAU", "LPAAW", "LPBB", "LPBBU",
    "LPBBW", "LPCN", "LPCV", "LPCVU", "LPCVW", "LPLA", "LPRO", "LPSN", "LPTH", "LQ",
    "LQDA", "LQDT", "LRCX", "LRE", "LRGE", "LRHC", "LRMR", "LRND", "LSAK", "LSBK",
    "LSCC", "LSE", "LSH", "LSTA", "LSTR", "LTBR", "LTCC", "LTGRU", "LTRN", "LTRX",
    "LTRYW", "LUCD", "LUCY", "LUCYW", "LULG", "LULU", "LUNG", "LUNR", "LVDS", "LVHD",
    "LVIG", "LVLU", "LVO", "LWAC", "LWACU", "LWACW", "LWAY", "LWLG", "LX", "LXEH",
    "LXEO", "LXRX", "LYEL", "LYFT", "LYTS", "LZ", "LZMH", "MAAS", "MAAY", "MACI",
    "MACIU", "MACIW", "MAGH", "MAKO", "MAMA", "MAMK", "MAMO", "MANH", "MAR", "MARA",
    "MARPS", "MASI", "MASK", "MASS", "MAT", "MATE", "MATH", "MATW", "MAXI", "MAYS",
    "MAZE", "MB", "MBAI", "MBAV", "MBAVU", "MBAVW", "MBB", "MBBC", "MBIN", "MBINL",
    "MBINM", "MBINN", "MBIO", "MBLY", "MBNKO", "MBOT", "MBRX", "MBS", "MBUU", "MBVI",
    "MBVIU", "MBVIW", "MBWM", "MBX", "MCAHU", "MCBS", "MCDS", "MCFT", "MCGA", "MCGAU",
    "MCGAW", "MCHB", "MCHI", "MCHP", "MCHPP", "MCHS", "MCHX", "MCRB", "MCRI", "MCTA",
    "MDAI", "MDAIW", "MDB", "MDBH", "MDCX", "MDCXW", "MDGL", "MDIA", "MDIV", "MDLN",
    "MDLZ", "MDRR", "MDWD", "MDXG", "MDXH", "MEDP", "MEDX", "MEGL", "MEHA", "MELI",
    "MEMA", "MEMS", "MENS", "MEOH", "MERC", "MESH", "MESHU", "MESHW", "MESO", "META",
    "METC", "METCB", "METCI", "METCZ", "METD", "METL", "METU", "MEVO", "MEVOU", "MEVOW",
    "MFI", "MFIC", "MFICL", "MFIG", "MFIN", "MFLX", "MFMO", "MFVL", "MGEE", "MGIH",
    "MGN", "MGNI", "MGNX", "MGPI", "MGRC", "MGRT", "MGRX", "MGTX", "MGX", "MGYR",
    "MIDD", "MILN", "MIMI", "MIND", "MIRA", "MIRM", "MIST", "MITK", "MKAM", "MKDW",
    "MKDWW", "MKLY", "MKLYR", "MKLYU", "MKSI", "MKTW", "MKTX", "MKZR", "MLAA", "MLAAU",
    "MLAAW", "MLAB", "MLAC", "MLACR", "MLACU", "MLCI", "MLCIL", "MLCO", "MLEC", "MLECW",
    "MLGO", "MLKN", "MLTX", "MLYS", "MMED", "MMLP", "MMSI", "MMTX", "MMTXU", "MMTXW",
    "MMYT", "MNDO", "MNDR", "MNDY", "MNKD", "MNOV", "MNPR", "MNRO", "MNSB", "MNSBP",
    "MNST", "MNTK", "MNTS", "MNTSW", "MNVT", "MNY", "MNYWW", "MNZL", "MOB", "MOBBW",
    "MOBI", "MOBX", "MOBXW", "MODD", "MODL", "MOLN", "MOMO", "MOOD", "MORN", "MOVE",
    "MPAA", "MPB", "MPG", "MPLT", "MPWR", "MQ", "MQQQ", "MRA", "MRAL", "MRAM",
    "MRBK", "MRCY", "MRDN", "MREO", "MRKR", "MRLN", "MRM", "MRNA", "MRNO", "MRNOW",
    "MRTN", "MRVI", "MRVL", "MRVU", "MRX", "MSAI", "MSAIW", "MSBI", "MSBIP", "MSDD",
    "MSEX", "MSFD", "MSFL", "MSFT", "MSFU", "MSGM", "MSGY", "MSLE", "MSR", "MSS",
    "MST", "MSTP", "MSTR", "MSTX", "MSW", "MTC", "MTCH", "MTEK", "MTEKW", "MTEN",
    "MTEX", "MTLS", "MTRX", "MTSI", "MTVA", "MTYY", "MU", "MUD", "MULL", "MULT",
    "MUU", "MUYY", "MUZE", "MUZEU", "MUZEW", "MVBF", "MVIS", "MVLL", "MVST", "MVSTW",
    "MWC", "MWH", "MWYN", "MXCT", "MXL", "MYCF", "MYCG", "MYCH", "MYCI", "MYCJ",
    "MYCK", "MYCL", "MYCM", "MYCN", "MYCO", "MYFW", "MYGN", "MYHA", "MYHB", "MYHC",
    "MYHD", "MYHE", "MYMF", "MYMG", "MYMH", "MYMI", "MYMJ", "MYMK", "MYPS", "MYPSW",
    "MYRG", "MYSE", "MYSEW", "MYSZ", "MYX", "MYXXR", "MYXXU", "MYXXW", "MZTI", "NA",
    "NAAS", "NAGE", "NAII", "NAKA", "NAMI", "NAMM", "NAMMW", "NAMS", "NAMSW", "NATH",
    "NATO", "NATR", "NAUT", "NAVI", "NAVN", "NB", "NBBK", "NBIG", "NBIL", "NBIS",
    "NBIX", "NBN", "NBP", "NBRG", "NBRGR", "NBRGU", "NBTB", "NBTX", "NCEL", "NCEW",
    "NCI", "NCIQ", "NCMI", "NCNA", "NCNO", "NCPB", "NCPL", "NCPLW", "NCRA", "NCSM",
    "NCT", "NCTY", "NDAA", "NDAQ", "NDLS", "NDRA", "NDSN", "NECB", "NEGG", "NEMG",
    "NEO", "NEOG", "NEON", "NEOV", "NEOVW", "NEPH", "NERV", "NESR", "NETG", "NEUP",
    "NEWT", "NEWTG", "NEWTH", "NEWTI", "NEWTO", "NEWTP", "NEWZ", "NEXM", "NEXN", "NEXR",
    "NEXRW", "NEXT", "NFBK", "NFE", "NFLX", "NFRX", "NFTY", "NFXL", "NFXS", "NGEN",
    "NGHT", "NGNE", "NHIC", "NHICU", "NHICW", "NHIV", "NHIVU", "NHIVW", "NHP", "NHPAP",
    "NHPBP", "NHTC", "NICE", "NICM", "NIKL", "NIOBW", "NIOG", "NIPG", "NIU", "NIVF",
    "NIVFW", "NIXT", "NIXX", "NIXXW", "NKLR", "NKSH", "NKTR", "NKTX", "NMFC", "NMFCZ",
    "NMIH", "NMP", "NMPAR", "NMPAU", "NMRA", "NMRK", "NMTC", "NN", "NNAVW", "NNBR",
    "NNDM", "NNE", "NNNN", "NNOX", "NODK", "NOEM", "NOEMR", "NOEMU", "NOEMW", "NOMA",
    "NOTV", "NOVT", "NOVTU", "NOWL", "NPAC", "NPACU", "NPACW", "NPCE", "NPFI", "NPT",
    "NRC", "NRDS", "NRES", "NRIM", "NRIX", "NRSN", "NRSNW", "NRXP", "NSI", "NSIT",
    "NSPR", "NSSC", "NSTS", "NSYS", "NTAP", "NTCL", "NTCT", "NTES", "NTGR", "NTHI",
    "NTIC", "NTLA", "NTNX", "NTRA", "NTRB", "NTRBW", "NTRP", "NTRS", "NTRSO", "NTSK",
    "NTWK", "NTWO", "NTWOU", "NTWOW", "NUAI", "NUAIW", "NUCL", "NUCLW", "NUG", "NUGY",
    "NUSB", "NUTR", "NUTX", "NUVL", "NUWE", "NVAX", "NVCR", "NVCT", "NVD", "NVDA",
    "NVDD", "NVDG", "NVDL", "NVDS", "NVDU", "NVEC", "NVMI", "NVNI", "NVNIW", "NVNO",
    "NVTS", "NVVE", "NVX", "NVYY", "NWBI", "NWE", "NWFL", "NWGL", "NWL", "NWPX",
    "NWS", "NWSA", "NWTG", "NXGL", "NXGLW", "NXL", "NXPI", "NXPL", "NXST", "NXT",
    "NXTC", "NXTG", "NXTS", "NXTT", "NXXT", "NYAX", "NYXH", "NZAC", "OABI", "OABIW",
    "OACC", "OACCU", "OACCW", "OBA", "OBAI", "OBAWU", "OBAWW", "OBIL", "OBIO", "OBT",
    "OBTC", "OCC", "OCCI", "OCCIM", "OCCIN", "OCFC", "OCG", "OCGN", "OCS", "OCSAW",
    "OCSL", "OCTV", "OCUL", "ODD", "ODDS", "ODFL", "ODTE", "ODTX", "ODVWZ", "ODYS",
    "OESX", "OFAL", "OFIX", "OFLX", "OFS", "OFSSH", "OFSSO", "OGI", "OHAC", "OHACR",
    "OHACU", "OIM", "OIMAU", "OIMAW", "OIO", "OIOWW", "OKLL", "OKTA", "OKTG", "OKUR",
    "OKYO", "OLB", "OLED", "OLLI", "OLMA", "OLOX", "OLPX", "OM", "OMAB", "OMCL",
    "OMDA", "OMER", "OMEX", "OMH", "OMSE", "ON", "ONB", "ONBPO", "ONBPP", "ONC",
    "ONCH", "ONCHU", "ONCHW", "ONCO", "ONCY", "ONDG", "ONDS", "ONEG", "ONEQ", "ONEW",
    "ONFO", "ONFOW", "ONMD", "ONMDW", "OPAL", "OPBK", "OPCH", "OPEG", "OPEN", "OPENL",
    "OPENW", "OPENZ", "OPK", "OPPJ", "OPRA", "OPRT", "OPRX", "OPTH", "OPTX", "OPTXW",
    "OPTZ", "OPXS", "ORBS", "ORBX", "ORCS", "ORCU", "ORCX", "ORGN", "ORGNW", "ORGO",
    "ORIC", "ORIO", "ORIQ", "ORIQU", "ORIQW", "ORIS", "ORKA", "ORKT", "ORLG", "ORLY",
    "ORMP", "ORR", "ORRF", "OSBC", "OSCG", "OSCX", "OSIS", "OSPN", "OSRH", "OSRHW",
    "OSS", "OST", "OSUR", "OSW", "OTEX", "OTGA", "OTGAU", "OTGAW", "OTGL", "OTLK",
    "OTLY", "OTTR", "OUST", "OVBC", "OVID", "OVLY", "OWLS", "OXBR", "OXBRW", "OXLC",
    "OXLCG", "OXLCI", "OXLCL", "OXLCM", "OXLCN", "OXLCO", "OXLCZ", "OXSQ", "OXSQG", "OXSQH",
    "OYSE", "OYSER", "OYSEU", "OZEM", "OZK", "OZKAP", "PAA", "PAAC", "PAACU", "PAACW",
    "PABD", "PABU", "PACB", "PACH", "PACHU", "PACHW", "PAGP", "PAHC", "PAL", "PALD",
    "PALI", "PALO", "PALOU", "PALOW", "PALU", "PAMT", "PANG", "PANL", "PANW", "PARK",
    "PASG", "PASW", "PATK", "PATN", "PAVM", "PAVS", "PAX", "PAYO", "PAYP", "PAYS",
    "PAYX", "PBEU", "PBFS", "PBHC", "PBK", "PBM", "PBMWW", "PBOG", "PBPH", "PBQQ",
    "PBRG", "PBYI", "PC", "PCAP", "PCAPU", "PCAPW", "PCAR", "PCB", "PCLA", "PCMM",
    "PCPI", "PCRX", "PCSA", "PCSC", "PCT", "PCTTU", "PCTTW", "PCTY", "PCVX", "PCYO",
    "PDBA", "PDBC", "PDC", "PDD", "PDDL", "PDEX", "PDFS", "PDLB", "PDP", "PDSB",
    "PDYN", "PDYNW", "PEBK", "PEBO", "PECE", "PECER", "PECEU", "PECEW", "PECO", "PEGA",
    "PENG", "PENN", "PEP", "PEPG", "PEPS", "PERI", "PESI", "PETS", "PETZ", "PEY",
    "PEZ", "PFAI", "PFBC", "PFDE", "PFF", "PFG", "PFI", "PFIS", "PFM", "PFOE",
    "PFSA", "PFX", "PFXNZ", "PGAC", "PGACR", "PGACU", "PGC", "PGEN", "PGJ", "PGNY",
    "PGY", "PGYWW", "PHAR", "PHAT", "PHIO", "PHO", "PHOE", "PHUN", "PHVS", "PI",
    "PICS", "PID", "PIE", "PIII", "PIIIW", "PIO", "PIZ", "PKBK", "PKOH", "PKW",
    "PLA", "PLAB", "PLAY", "PLBC", "PLBL", "PLBY", "PLCE", "PLMK", "PLMKU", "PLMKW",
    "PLMR", "PLPC", "PLRX", "PLRZ", "PLSE", "PLSM", "PLTD", "PLTG", "PLTK", "PLTR",
    "PLTS", "PLTU", "PLTZ", "PLUG", "PLUL", "PLUR", "PLUS", "PLUT", "PLXS", "PLYX",
    "PLYY", "PMAX", "PMBS", "PMCB", "PMEC", "PMN", "PMTR", "PMTRU", "PMTRW", "PMTS",
    "PMVP", "PN", "PNBK", "PNQI", "PNRG", "PNTG", "POCI", "PODC", "PODD", "POET",
    "POLA", "POLE", "POLEU", "POLEW", "POM", "PONO", "PONOR", "PONOU", "PONY", "POOL",
    "POWI", "POWL", "POWW", "POWWP", "PPBT", "PPC", "PPCB", "PPH", "PPHC", "PPI",
    "PPIH", "PPLI", "PPSI", "PPTA", "PQAP", "PQJA", "PQJL", "PQOC", "PRAA", "PRAX",
    "PRCH", "PRCT", "PRDO", "PRE", "PRENW", "PRFX", "PRFZ", "PRGS", "PRHI", "PRHIZ",
    "PRLD", "PRME", "PRMR", "PRN", "PROF", "PROK", "PROP", "PROV", "PRPL", "PRPO",
    "PRQR", "PRSO", "PRTA", "PRTH", "PRTS", "PRVA", "PRZO", "PSC", "PSCC", "PSCD",
    "PSCE", "PSCF", "PSCH", "PSCI", "PSCM", "PSCT", "PSCU", "PSEC", "PSET", "PSHG",
    "PSIG", "PSIX", "PSKY", "PSL", "PSMT", "PSNL", "PSNY", "PSNYW", "PSTR", "PSTV",
    "PSWD", "PTACU", "PTC", "PTCT", "PTEN", "PTF", "PTGX", "PTH", "PTIR", "PTLE",
    "PTLO", "PTN", "PTNM", "PTNQ", "PTON", "PTOR", "PTORU", "PTORW", "PTRN", "PUBM",
    "PUI", "PULM", "PURR", "PUSA", "PVLA", "PWP", "PWRD", "PWRL", "PXI", "PXLW",
    "PXS", "PY", "PYPD", "PYPG", "PYPL", "PYXS", "PYZ", "PZZA", "QABA", "QADR",
    "QADRU", "QADRW", "QALT", "QAT", "QB", "QBIG", "QBTZ", "QBUF", "QBY", "QCLN",
    "QCLR", "QCLS", "QCMD", "QCML", "QCMU", "QCOM", "QCRH", "QDEL", "QDTY", "QETA",
    "QETAR", "QETAU", "QEW", "QFIN", "QGRD", "QH", "QHDG", "QLDY", "QLYS", "QMCO",
    "QMID", "QMMM", "QMOM", "QNCX", "QNRX", "QNST", "QNT", "QNTM", "QNXT", "QOWZ",
    "QPUX", "QQA", "QQDN", "QQEW", "QQHG", "QQLV", "QQMG", "QQQ", "QQQA", "QQQE",
    "QQQG", "QQQH", "QQQI", "QQQJ", "QQQM", "QQQP", "QQQS", "QQQT", "QQQX", "QQQY",
    "QQUP", "QQWZ", "QQXL", "QQXT", "QRHC", "QRMI", "QRVO", "QS", "QSEA", "QSEAR",
    "QSEAU", "QSI", "QSIAW", "QSIX", "QSML", "QTEC", "QTEX", "QTEXW", "QTI", "QTOP",
    "QTR", "QTRX", "QTTB", "QTUM", "QUBT", "QUCY", "QUIK", "QUMS", "QUMSR", "QUMSU",
    "QURE", "QVAL", "QVOL", "QXL", "QXQ", "QYLD", "QYLG", "RAA", "RAAQ", "RAAQU",
    "RAAQW", "RACC", "RADX", "RAIL", "RAIN", "RAINW", "RAND", "RANG", "RANGR", "RANGU",
    "RANI", "RAPP", "RARE", "RAUS", "RAVE", "RAY", "RAYA", "RBB", "RBBN", "RBCAA",
    "RBIL", "RBKB", "RBNE", "RCAT", "RCAX", "RCEL", "RCGE", "RCKT", "RCKTW", "RCKY",
    "RCMT", "RCON", "RCT", "RDAC", "RDACR", "RDACU", "RDAG", "RDAGU", "RDAGW", "RDCM",
    "RDGT", "RDHL", "RDI", "RDIB", "RDNT", "RDNW", "RDTL", "RDTY", "RDVT", "RDVY",
    "RDWR", "RDZN", "RDZNW", "REAI", "REAL", "REAX", "REBN", "RECT", "REE", "REFI",
    "REFR", "REG", "REGCO", "REGCP", "REGN", "REIT", "REKR", "RELL", "RELY", "REMG",
    "RENT", "RENX", "REPL", "RETO", "REVB", "REVBW", "REXC", "REYN", "RFAI", "RFAIR",
    "RFAIU", "RFAM", "RFAMR", "RFAMU", "RFDI", "RFEM", "RFIL", "RGC", "RGCO", "RGEN",
    "RGLD", "RGLO", "RGNX", "RGP", "RGS", "RGTI", "RGTIW", "RGTX", "RGTZ", "RGYY",
    "RIBB", "RIBBR", "RIBBU", "RICK", "RIFR", "RIGL", "RILY", "RILYG", "RILYL", "RILYN",
    "RILYP", "RILYT", "RILYZ", "RIME", "RING", "RINT", "RIOT", "RITR", "RIVN", "RJET",
    "RKDA", "RKLB", "RKLX", "RKLZ", "RKNG", "RKTO", "RLAY", "RLMD", "RLYB", "RMBI",
    "RMBS", "RMCF", "RMCO", "RMCOW", "RMIX", "RMNI", "RMR", "RMSG", "RMSGW", "RMTI",
    "RNA", "RNAC", "RNAZ", "RNEM", "RNGT", "RNGTU", "RNGTW", "RNIN", "RNRG", "RNTX",
    "RNW", "RNWWW", "RNXT", "ROAD", "ROBT", "ROC", "ROCK", "ROCQ", "ROCY", "ROE",
    "ROIV", "ROKU", "ROMA", "ROOT", "ROP", "ROST", "RPAY", "RPD", "RPGL", "RPID",
    "RPRX", "RR", "RRBI", "RREV", "RREVU", "RREVW", "RRGB", "RRR", "RSSS", "RSVR",
    "RSVRW", "RTAC", "RTACU", "RTACW", "RTB", "RTH", "RTXG", "RTYY", "RUBI", "RUM",
    "RUMBW", "RUN", "RUNN", "RUSC", "RUSHA", "RUSHB", "RVMD", "RVMDW", "RVNL", "RVSB",
    "RVSN", "RVSNW", "RWAY", "RWAYI", "RWAYL", "RWIN", "RXRX", "RXST", "RXT", "RYAAY",
    "RYET", "RYM", "RYOJ", "RYTM", "RZLT", "RZLV", "RZLVW", "SAAQ", "SAAQU", "SAAQW",
    "SABR", "SABS", "SABSW", "SAFT", "SAFX", "SAGT", "SAIA", "SAIC", "SAIH", "SAIHW",
    "SAIL", "SAMG", "SANA", "SANG", "SANM", "SARK", "SATA", "SATG", "SATL", "SATLW",
    "SATS", "SBAC", "SBC", "SBCF", "SBCWW", "SBET", "SBFG", "SBFM", "SBFMW", "SBGI",
    "SBLK", "SBRA", "SBU", "SBUX", "SCA", "SCAG", "SCAGW", "SCDS", "SCHL", "SCII",
    "SCIIR", "SCIIU", "SCKT", "SCLS", "SCLX", "SCLXW", "SCNI", "SCNX", "SCOR", "SCPQ",
    "SCPQU", "SCPQW", "SCSC", "SCVL", "SCWO", "SCYX", "SCZ", "SCZM", "SDA", "SDAWW",
    "SDG", "SDGR", "SDHI", "SDHIR", "SDHIU", "SDM", "SDOT", "SDSI", "SDST", "SDSTW",
    "SDTY", "SDVY", "SEAT", "SEATW", "SEDG", "SEED", "SEEM", "SEER", "SEGG", "SEIC",
    "SEIE", "SEIS", "SELF", "SEMY", "SENEA", "SENEB", "SENS", "SEPN", "SERA", "SERV",
    "SETM", "SEV", "SEVN", "SEZL", "SFBC", "SFD", "SFHG", "SFIX", "SFLO", "SFM",
    "SFNC", "SFST", "SFWL", "SGA", "SGC", "SGHT", "SGLY", "SGML", "SGMT", "SGP",
    "SGRP", "SGRY", "SHAZ", "SHBI", "SHC", "SHEN", "SHFS", "SHFSW", "SHIM", "SHIP",
    "SHLS", "SHMD", "SHMDW", "SHOO", "SHOP", "SHPH", "SHPU", "SHRY", "SHY", "SIBN",
    "SIDU", "SIEB", "SIFY", "SIGA", "SIGI", "SIGIP", "SILC", "SILO", "SIMA", "SIMAU",
    "SIMAW", "SIMO", "SINT", "SION", "SIRI", "SITM", "SJ", "SJCP", "SJLD", "SKBL",
    "SKIN", "SKK", "SKOR", "SKRE", "SKWD", "SKYA", "SKYAW", "SKYE", "SKYQ", "SKYT",
    "SKYU", "SKYW", "SKYX", "SKYY", "SLAB", "SLDB", "SLDE", "SLDP", "SLDPW", "SLE",
    "SLGB", "SLGL", "SLM", "SLMBP", "SLMT", "SLN", "SLNG", "SLNH", "SLNHP", "SLP",
    "SLQD", "SLRC", "SLS", "SLSN", "SLVO", "SLVR", "SLXN", "SLXNW", "SMBC", "SMCF",
    "SMCI", "SMCL", "SMCO", "SMCX", "SMCZ", "SMH", "SMHX", "SMID", "SMMT", "SMOM",
    "SMPL", "SMRI", "SMSI", "SMST", "SMTC", "SMTI", "SMTK", "SMX", "SMXT", "SMXWW",
    "SMYY", "SNAG", "SNAL", "SNBR", "SND", "SNDK", "SNDL", "SNDX", "SNES", "SNEX",
    "SNFCA", "SNGX", "SNOA", "SNPS", "SNSE", "SNSR", "SNT", "SNTG", "SNTI", "SNWV",
    "SNY", "SNYR", "SOBR", "SOCA", "SOCAU", "SOCAW", "SOCL", "SOFA", "SOFI", "SOFX",
    "SOGP", "SOHU", "SOLC", "SOLS", "SOLT", "SOLZ", "SONM", "SONO", "SOPH", "SORA",
    "SORN", "SORNU", "SORNW", "SOTK", "SOUN", "SOUNW", "SOUX", "SOWG", "SOXQ", "SOXX",
    "SPAI", "SPAM", "SPAQ", "SPBC", "SPCB", "SPCK", "SPCT", "SPEG", "SPEGR", "SPEGU",
    "SPFI", "SPHL", "SPIT", "SPKL", "SPKLU", "SPKLW", "SPOG", "SPOK", "SPPL", "SPRB",
    "SPRC", "SPRO", "SPRX", "SPRY", "SPSC", "SPT", "SPTX", "SPWH", "SPWR", "SPWRW",
    "SPXD", "SPYQ", "SQFT", "SQFTP", "SQFTW", "SQLV", "SQQQ", "SQS", "SRAD", "SRBK",
    "SRCE", "SRET", "SRPT", "SRRK", "SRTA", "SRTS", "SRZN", "SRZNW", "SSAC", "SSACR",
    "SSACU", "SSACW", "SSBI", "SSEA", "SSEAR", "SSEAU", "SSII", "SSM", "SSNC", "SSP",
    "SSRM", "SSS", "SSSS", "SSSSL", "SSTI", "SSYS", "STAA", "STAK", "STBA", "STEP",
    "STEX", "STFS", "STGW", "STHO", "STI", "STIM", "STKE", "STKH", "STKS", "STLD",
    "STNC", "STNE", "STOK", "STRA", "STRC", "STRD", "STRF", "STRK", "STRL", "STRO",
    "STRR", "STRRP", "STRS", "STRT", "STRZ", "STTK", "STX", "SUGP", "SUIG", "SUIS",
    "SUJA", "SUMA", "SUMAR", "SUMAU", "SUNE", "SUNS", "SUPN", "SUPP", "SUPX", "SURG",
    "SUSB", "SUSC", "SUSL", "SVA", "SVAC", "SVACU", "SVACW", "SVAQ", "SVAQU", "SVAQW",
    "SVC", "SVCC", "SVCCU", "SVCCW", "SVCO", "SVIV", "SVIVU", "SVIVW", "SVRA", "SVRE",
    "SVREW", "SVRN", "SWAG", "SWAGW", "SWBI", "SWIM", "SWKHL", "SWKS", "SWMR", "SWP",
    "SWVL", "SWVLW", "SXTC", "SXTP", "SXTPW", "SY", "SYBT", "SYM", "SYNA", "SYPR",
    "SYRE", "SYZ", "SZZL", "SZZLR", "SZZLU", "TACH", "TACHU", "TACHW", "TACO", "TACOU",
    "TACOW", "TACT", "TALK", "TALKW", "TANH", "TAOP", "TAOX", "TAOZ", "TARA", "TARK",
    "TARS", "TASK", "TATT", "TAVI", "TAVIR", "TAVIU", "TAX", "TAXE", "TAXI", "TAXS",
    "TAXT", "TAYD", "TBBK", "TBCH", "TBH", "TBIL", "TBLA", "TBLAW", "TBLD", "TBPH",
    "TBRG", "TC", "TCAN", "TCBI", "TCBIO", "TCBK", "TCBS", "TCHI", "TCMD", "TCOM",
    "TCPC", "TCRT", "TCRX", "TCX", "TDAC", "TDACU", "TDACW", "TDI", "TDIC", "TDIV",
    "TDOG", "TDOT", "TDSB", "TDSC", "TDTH", "TDUP", "TDWD", "TDWDR", "TDWDU", "TEAD",
    "TEAM", "TECH", "TECX", "TECY", "TEKX", "TEKY", "TELA", "TELO", "TEM", "TENB",
    "TENX", "TER", "TERG", "TEXN", "TEXX", "TFGZ", "TFNS", "TFSL", "TGHL", "TGL",
    "TGTX", "TH", "THCH", "THFF", "THH", "THMZ", "THRM", "THRV", "THRY", "THYM",
    "THYP", "TIGO", "TIGR", "TIL", "TILE", "TIPT", "TITN", "TJGC", "TKLF", "TKNO",
    "TKNS", "TLA", "TLF", "TLG", "TLIH", "TLN", "TLNC", "TLNCU", "TLNCW", "TLPH",
    "TLRY", "TLS", "TLSA", "TLSI", "TLSIW", "TLT", "TLX", "TMB", "TMC", "TMCI",
    "TMCR", "TMCWW", "TMDX", "TMED", "TMNL", "TMNS", "TMSF", "TMTS", "TMTSU", "TMTSW",
    "TMUS", "TMUSI", "TMUSL", "TMUSZ", "TMYY", "TNDM", "TNGX", "TNMG", "TNON", "TNONW",
    "TNXP", "TNXT", "TNYA", "TOI", "TOIIW", "TOMZ", "TONX", "TOP", "TORO", "TOUR",
    "TOWN", "TOYO", "TPCS", "TPG", "TPGXL", "TPLS", "TPST", "TQQQ", "TQQY", "TRAW",
    "TRAX", "TRBF", "TRDA", "TREE", "TRGS", "TRGSR", "TRGSU", "TRI", "TRIB", "TRIN",
    "TRINI", "TRINZ", "TRIP", "TRMB", "TRMD", "TRMK", "TRNR", "TRNS", "TRON", "TROO",
    "TROW", "TRS", "TRSG", "TRST", "TRUC", "TRUD", "TRUF", "TRUG", "TRUH", "TRUI",
    "TRUO", "TRUP", "TRUT", "TRVG", "TRVI", "TSAT", "TSBK", "TSCM", "TSCO", "TSDD",
    "TSEL", "TSEM", "TSHA", "TSL", "TSLA", "TSLG", "TSLL", "TSLQ", "TSLR", "TSLS",
    "TSMG", "TSMU", "TSMX", "TSMZ", "TSPY", "TSSI", "TSUI", "TSYX", "TSYY", "TTAN",
    "TTD", "TTEC", "TTEK", "TTEQ", "TTGT", "TTMI", "TTRX", "TTWO", "TUG", "TUGN",
    "TULP", "TUR", "TURB", "TURF", "TUSK", "TVA", "TVACU", "TVACW", "TVAI", "TVAIR",
    "TVAIU", "TVGN", "TVGNW", "TVRD", "TVTX", "TW", "TWAV", "TWFG", "TWG", "TWIN",
    "TWLV", "TWLVR", "TWLVU", "TWST", "TXG", "TXMD", "TXN", "TXRH", "TXUE", "TXUG",
    "TXXD", "TXXH", "TXXS", "TYGO", "TYRA", "TZOO", "UAE", "UAL", "UBCP", "UBND",
    "UBRL", "UBSI", "UBXG", "UCAR", "UCFI", "UCFIW", "UCL", "UCRD", "UCTT", "UCYB",
    "UECG", "UEIC", "UEVM", "UFCS", "UFG", "UFIV", "UFO", "UFOX", "UFPI", "UFPT",
    "UG", "UGRO", "UITB", "UIVM", "UK", "ULBI", "ULCC", "ULH", "ULTA", "ULTI",
    "ULVM", "UMBF", "UMBFO", "UMMA", "UNB", "UNCY", "UNHG", "UNIT", "UNIY", "UNTY",
    "UONE", "UONEK", "UPB", "UPBD", "UPC", "UPGR", "UPLD", "UPSG", "UPST", "UPWK",
    "UPXI", "URBN", "URGN", "URNJ", "UROY", "USAF", "USAR", "USAU", "USCB", "USCL",
    "USDX", "USEA", "USFI", "USGG", "USGO", "USIG", "USIN", "USIO", "USLM", "USMC",
    "USOI", "USOY", "USRD", "USSH", "USTB", "USVM", "USVN", "USXF", "UTEN", "UTHR",
    "UTHY", "UTMD", "UTRE", "UTSI", "UTWO", "UTWY", "UUUG", "UVSP", "UXIN", "UYLD",
    "UYSC", "UYSCR", "UYSCU", "UZX", "VABK", "VACH", "VACHU", "VACHW", "VALG", "VALN",
    "VALU", "VANI", "VAVX", "VBCA", "VBCB", "VBCC", "VBCD", "VBCE", "VBCF", "VBCG",
    "VBCH", "VBCI", "VBCJ", "VBIL", "VBIO", "VBNB", "VBNK", "VC", "VCEL", "VCIG",
    "VCIT", "VCLT", "VCRB", "VCSH", "VCTR", "VCYT", "VECO", "VEEA", "VEEAW", "VEEE",
    "VEFA", "VELO", "VEON", "VERA", "VERI", "VERU", "VERX", "VFF", "VFLO", "VFS",
    "VFSWW", "VGAS", "VGASW", "VGIT", "VGLT", "VGSH", "VGSR", "VGUS", "VHC", "VHCP",
    "VHCPU", "VHCPW", "VHUB", "VIASP", "VIAV", "VICR", "VIGI", "VINP", "VIOT", "VIR",
    "VIRC", "VISN", "VITL", "VIVK", "VIVO", "VIVS", "VKTX", "VLGEA", "VLY", "VLYPN",
    "VLYPO", "VLYPP", "VMAR", "VMBS", "VMD", "VMET", "VNCE", "VNDA", "VNET", "VNME",
    "VNMEU", "VNMEW", "VNOM", "VNQI", "VOD", "VOLT", "VONE", "VONG", "VONV", "VOR",
    "VOTE", "VOXR", "VPLS", "VRA", "VRAX", "VRCA", "VRDN", "VREX", "VRIG", "VRM",
    "VRME", "VRNS", "VRRM", "VRSK", "VRSN", "VRTL", "VRTX", "VS", "VSA", "VSAT",
    "VSDA", "VSEC", "VSECU", "VSEE", "VSEEW", "VSME", "VSMV", "VSNT", "VSOL", "VSTD",
    "VSTL", "VSTM", "VTC", "VTGN", "VTHR", "VTIP", "VTIX", "VTRS", "VTSI", "VTVT",
    "VTWG", "VTWO", "VTWV", "VUZI", "VVOS", "VWAV", "VWAVW", "VWOB", "VXUS", "VYGR",
    "VYMI", "VYNE", "WABC", "WABF", "WAFD", "WAFDP", "WAFU", "WAI", "WALD", "WALDW",
    "WAMA", "WARP", "WASH", "WATT", "WAVE", "WAY", "WB", "WBD", "WBTN", "WBUY",
    "WCBR", "WCLD", "WCT", "WDAF", "WDAY", "WDC", "WDFC", "WDGF", "WEEI", "WEN",
    "WENN", "WENNU", "WENNW", "WERN", "WEST", "WETH", "WETO", "WEYS", "WFCF", "WFF",
    "WFRD", "WGMI", "WGRX", "WGS", "WGSWW", "WHF", "WHFCL", "WHLR", "WHLRD", "WHLRL",
    "WHLRP", "WHWK", "WILC", "WIMA", "WIMI", "WINA", "WING", "WISE", "WIX", "WKEY",
    "WKHS", "WKSP", "WLDN", "WLDS", "WLDSW", "WLFC", "WLII", "WLIIU", "WLIIW", "WLTH",
    "WMG", "WMT", "WNEB", "WNW", "WOK", "WOOD", "WOOF", "WPRT", "WRAP", "WRD",
    "WRLD", "WRND", "WRTH", "WSBC", "WSBCO", "WSBF", "WSBK", "WSC", "WSE", "WSFS",
    "WSGE", "WSHP", "WSML", "WSTN", "WSTNR", "WSTNU", "WTBA", "WTBN", "WTF", "WTFC",
    "WTFCN", "WTG", "WTGUR", "WTGUU", "WTIP", "WTMU", "WTMY", "WTO", "WTW", "WULF",
    "WVE", "WVVI", "WVVIP", "WW", "WWD", "WXM", "WYFI", "WYHG", "WYNN", "XAIR",
    "XAIX", "XBCI", "XBIL", "XBIO", "XBIT", "XBP", "XBPEW", "XBTY", "XCBE", "XCBEU",
    "XCBEW", "XCH", "XCNY", "XCUR", "XDEF", "XE", "XEL", "XELB", "XELLL", "XENE",
    "XERS", "XEY", "XFOR", "XGN", "XHG", "XHLD", "XLO", "XMAG", "XMAX", "XMTR",
    "XNCR", "XNDU", "XNET", "XOMA", "XOMAO", "XOMAP", "XOMX", "XOS", "XOSWW", "XOVR",
    "XP", "XPEG", "XPEL", "XPON", "XQQI", "XRAY", "XRPC", "XRPI", "XRPN", "XRPNU",
    "XRPNW", "XRPT", "XRTX", "XRX", "XRXDW", "XSLL", "XSLLU", "XSLLW", "XSPI", "XT",
    "XTIA", "XTLB", "XWEL", "XXII", "XXX", "XYZG", "YAAS", "YB", "YBMN", "YBST",
    "YBTY", "YDDL", "YDES", "YDESW", "YDKG", "YHC", "YHGJ", "YHNA", "YHNAR", "YHNAU",
    "YI", "YIBO", "YJ", "YLDE", "YMAT", "YMT", "YNOT", "YOKE", "YOOV", "YORW",
    "YOUL", "YQ", "YQQQ", "YSPY", "YSWY", "YSXT", "YTRA", "YXT", "YYAI", "YYGH",
    "Z", "ZAP", "ZAZZT", "ZBAO", "ZBIO", "ZBRA", "ZBZZT", "ZCMD", "ZCZZT", "ZD",
    "ZDAI", "ZENA", "ZEO", "ZEOWW", "ZG", "ZHOG", "ZION", "ZIONP", "ZJK", "ZJYL",
    "ZJZZT", "ZKIN", "ZKP", "ZKPU", "ZKPW", "ZLAB", "ZM", "ZMUN", "ZNB", "ZNTL",
    "ZOOZ", "ZOOZW", "ZS", "ZSQR", "ZSTK", "ZTEK", "ZTEN", "ZTG", "ZTOP", "ZTRE",
    "ZTWO", "ZUMZ", "ZURA", "ZVRA", "ZVZZT", "ZWZZT", "ZXYZ.A", "ZXZZT", "ZYBT", "ZYME",
]

# ==========================================
# RSI FUNCTION
# ==========================================

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ==========================================
# TREND FUNCTION
# ==========================================

def get_trend(hist):
    closes = hist['Close'].tail(50)
    x = np.arange(len(closes))
    y = closes.values
    slope = np.polyfit(x, y, 1)[0]
    return "Uptrend" if slope > 0 else "Downtrend"

# ==========================================
# RELATIVE STRENGTH VS SPY
# ==========================================

def relative_strength(stock_hist, spy_hist):
    stock_return = (
        stock_hist['Close'].iloc[-1] - stock_hist['Close'].iloc[-20]
    ) / stock_hist['Close'].iloc[-20]
    spy_return = (
        spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[-20]
    ) / spy_hist['Close'].iloc[-20]
    return round(stock_return - spy_return, 4)

# ==========================================
# MARKET FILTER
# ==========================================

def market_is_bullish():
    spy = yf.Ticker("SPY").history(period="1y")
    qqq = yf.Ticker("QQQ").history(period="1y")
    spy['50EMA'] = spy['Close'].ewm(span=50).mean()
    spy['200EMA'] = spy['Close'].ewm(span=200).mean()
    qqq['50EMA'] = qqq['Close'].ewm(span=50).mean()
    qqq['200EMA'] = qqq['Close'].ewm(span=200).mean()
    spy_bull = spy['Close'].iloc[-1] > spy['50EMA'].iloc[-1] > spy['200EMA'].iloc[-1]
    qqq_bull = qqq['Close'].iloc[-1] > qqq['50EMA'].iloc[-1] > qqq['200EMA'].iloc[-1]
    return spy_bull and qqq_bull

# ==========================================
# WEB SCRAPED GROWTH
# ==========================================

def get_growth_estimate(stock):
    try:
        url = f'https://www.alphaquery.com/stock/{stock}/all-data-variables'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        pe = soup.find_all('td', class_='text-right')[164]
        peg = soup.find_all('td', class_='text-right')[166]
        growth = float(pe.text) / float(peg.text)
        return round(growth, 2)
    except:
        return None

# ==========================================
# BACKTEST FUNCTION
# ==========================================

def backtest(hist):
    wins = 0
    losses = 0
    total_return = 0
    hist = hist.copy()
    hist['20EMA'] = hist['Close'].ewm(span=20).mean()
    hist['50EMA'] = hist['Close'].ewm(span=50).mean()
    hist['200EMA'] = hist['Close'].ewm(span=200).mean()
    hist['RSI'] = calculate_rsi(hist['Close'])
    high_low = hist['High'] - hist['Low']
    high_close = abs(hist['High'] - hist['Close'].shift())
    low_close = abs(hist['Low'] - hist['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    hist['ATR'] = true_range.rolling(14).mean()
    for i in range(210, len(hist) - 10):
        row = hist.iloc[i]
        close = row['Close']
        ema20 = row['20EMA']
        ema50 = row['50EMA']
        ema200 = row['200EMA']
        rsi = row['RSI']
        atr = row['ATR']
        bullish = close > ema20 and ema20 > ema50 and ema50 > ema200
        pullback = close <= ema20 * 1.03
        healthy_rsi = 45 <= rsi <= 70
        if bullish and pullback and healthy_rsi:
            stop = close - (1.5 * atr)
            target = close + (3 * atr)
            future = hist.iloc[i+1:i+10]
            hit_target = False
            hit_stop = False
            for _, future_row in future.iterrows():
                low = future_row['Low']
                high = future_row['High']
                if low <= stop:
                    hit_stop = True
                    break
                if high >= target:
                    hit_target = True
                    break
            if hit_target:
                wins += 1
                total_return += 2
            elif hit_stop:
                losses += 1
                total_return -= 1
    total_trades = wins + losses
    win_rate = 0 if total_trades == 0 else round((wins / total_trades) * 100, 2)
    return {"Wins": wins, "Losses": losses, "Win Rate": win_rate, "Total Return R": total_return}

# ==========================================
# SCAN ENGINE
# ==========================================

def run_scan(stocks):
    print("\nADVANCED SWING TRADING SYSTEM - SCAN")
    print("=" * 120)
    bullish_market = market_is_bullish()
    if bullish_market:
        print("\nMARKET STATUS: BULLISH")
    else:
        print("\nMARKET STATUS: BEARISH")
        print("Avoiding long swing trades.\n")
    results = {
        'Stock': [], 'Price': [], 'Trend': [], 'RSI': [],
        'Relative Strength': [], 'Growth Estimate': [], 'Signal': [],
        'Entry': [], 'Stop Loss': [], 'Target': [],
        'Win Rate': [], 'Backtest Return': []
    }
    spy_hist = yf.Ticker("SPY").history(period="1y")
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            hist = ticker.history(period="1y")
            if len(hist) < 210:
                continue
            hist['20EMA'] = hist['Close'].ewm(span=20).mean()
            hist['50EMA'] = hist['Close'].ewm(span=50).mean()
            hist['200EMA'] = hist['Close'].ewm(span=200).mean()
            hist['RSI'] = calculate_rsi(hist['Close'])
            high_low = hist['High'] - hist['Low']
            high_close = abs(hist['High'] - hist['Close'].shift())
            low_close = abs(hist['Low'] - hist['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            hist['ATR'] = true_range.rolling(14).mean()
            latest = hist.iloc[-1]
            close = round(latest['Close'], 2)
            ema20 = latest['20EMA']
            ema50 = latest['50EMA']
            ema200 = latest['200EMA']
            rsi = round(latest['RSI'], 2)
            atr = latest['ATR']
            trend = get_trend(hist)
            rs = relative_strength(hist, spy_hist)
            growth = get_growth_estimate(stock)
            bullish_trend = close > ema20 and ema20 > ema50 and ema50 > ema200
            pullback_zone = close <= ema20 * 1.03
            healthy_rsi = 45 <= rsi <= 70
            outperforming_market = rs > 0
            if bullish_market and bullish_trend and pullback_zone and healthy_rsi and outperforming_market:
                signal = "BUY"
                entry = round(close, 2)
                stop_loss = round(close - (1.5 * atr), 2)
                target = round(close + (3 * atr), 2)
            else:
                signal = "NO TRADE"
                entry = None
                stop_loss = None
                target = None
            bt = backtest(hist)
            print(
                f"{stock:<6}${close:<10}{trend:<12}RS:{rs:<10}RSI:{rsi:<8}{signal:<12}WR:{bt['Win Rate']}%"
            )
            results['Stock'].append(stock)
            results['Price'].append(close)
            results['Trend'].append(trend)
            results['RSI'].append(rsi)
            results['Relative Strength'].append(rs)
            results['Growth Estimate'].append(growth)
            results['Signal'].append(signal)
            results['Entry'].append(entry)
            results['Stop Loss'].append(stop_loss)
            results['Target'].append(target)
            results['Win Rate'].append(bt['Win Rate'])
            results['Backtest Return'].append(bt['Total Return R'])
        except Exception as e:
            print(f"ERROR: {stock} -> {e}")
    df = pd.DataFrame(results)
    df.to_excel("advanced_swing_trades.xlsx", index=False)
    return df

# ==========================================
# CHERRY-PICK CANDIDATES
# ==========================================

def pick_top_candidates(df, max_picks=7):
    candidates = df[df['Signal'] == 'BUY'].copy()
    candidates = candidates.dropna(subset=['Entry', 'Target'])
    candidates = candidates[candidates['Target'] >= candidates['Entry'] * 1.15]
    candidates = candidates[(candidates['Win Rate'] >= 80) & (candidates['Win Rate'] <= 100)]
    candidates = candidates[candidates['Backtest Return'] >= 5]
    candidates = candidates.sort_values(by=['Win Rate', 'Backtest Return'], ascending=False)
    top = candidates.head(max_picks)
    top.to_excel("top_candidates.xlsx", index=False)
    return top

# ==========================================
# WEBULL LOGIN  ← matches your working test script exactly
# ==========================================

def webull_login():
    """
    Connects to Webull using the same pattern confirmed working in your test.
    Reads credentials from environment variables:
        WEBULL_APP_KEY
        WEBULL_APP_SECRET

    Returns (trade_client, account_id) where account_id is your
    Individual Margin account (INDIVIDUAL_MARGIN class), or the first
    account if that class isn't found.
    """
    app_key = os.environ.get("WEBULL_APP_KEY")
    app_secret = os.environ.get("WEBULL_APP_SECRET")

    if not app_key or not app_secret:
        raise RuntimeError(
            "Set WEBULL_APP_KEY and WEBULL_APP_SECRET environment variables before running."
        )

    # ---- same two lines that worked in your test ----
    api_client = ApiClient(app_key, app_secret, "us")
    trade_client = TradeClient(api_client)
    # -------------------------------------------------

    # Resolve account_id
    account_id = os.environ.get("WEBULL_ACCOUNT_ID")

    if not account_id:
        res = trade_client.account_v2.get_account_list()

        if res.status_code != 200:
            raise RuntimeError(f"Could not fetch account list: {res.text}")

        accounts = res.json()

        if not accounts:
            raise RuntimeError("No accounts returned for these credentials.")

        # Prefer Individual Margin; fall back to first account
        preferred = next(
            (a for a in accounts if a.get("account_class") == "INDIVIDUAL_MARGIN"),
            accounts[0]
        )

        account_id = preferred["account_id"]
        print(
            f"Using account: {preferred.get('account_label')} "
            f"| ID: {account_id} "
            f"| Type: {preferred.get('account_type')} "
            f"| Class: {preferred.get('account_class')}"
        )

    return trade_client, account_id

# ==========================================
# SHOW PORTFOLIO
# ==========================================

def show_portfolio(trade_client, account_id):
    print("\n" + "=" * 60)
    print("CURRENT PORTFOLIO")
    print("=" * 60)

    try:
        balance = trade_client.account_v2.get_account_balance(account_id).json()
        if "total_cash_balance" in balance:
            total_assets = balance.get("total_net_liquidation_value", "N/A")
            cash_balance = balance.get("total_cash_balance", "N/A")
        else:
            total_assets = balance.get("total_market_value", "N/A")
            cash_balance = "N/A"
        buying_power = balance.get("total_cash_balance") or balance.get("total_market_value", "N/A")
        print(f"Total Assets : ${total_assets}")
        print(f"Buying Power : ${buying_power}")
    except Exception as e:
        print(f"Could not fetch balance: {e}")

    pos_res = trade_client.account_v2.get_account_position(account_id)
    if pos_res.status_code == 200:
        positions = pos_res.json()
        if not positions:
            print("\nNo open positions.")
        else:
            print(f"\n{'Symbol':<8}{'Qty':<10}{'Avg Cost':<12}{'Last Price':<12}{'Mkt Value':<12}")
            for p in positions:
                print(
                    f"{p.get('symbol',''):<8}"
                    f"{p.get('quantity',''):<10}"
                    f"{p.get('cost_price',''):<12}"
                    f"{p.get('last_price',''):<12}"
                    f"{p.get('market_value',''):<12}"
                )
    else:
        print(f"Could not fetch positions: {pos_res.text}")

    print("=" * 60 + "\n")

# ==========================================
# PLACE BUY ORDER
# ==========================================

def place_buy_order(trade_client, account_id, symbol, dollar_amount, reference_price):
    """
    Sizes the order by dollar amount and submits a MARKET BUY
    through the Webull OpenAPI.
    """
    if not reference_price or reference_price <= 0:
        print(f"Could not determine a price for {symbol}. Skipping.")
        return None

    shares = math.floor(dollar_amount / reference_price)

    if shares < 1:
        print(
            f"${dollar_amount} is not enough to buy 1 share of {symbol} "
            f"at ~${reference_price}. Skipping."
        )
        return None

    print(
        f"\nSubmitting -> BUY {shares} share(s) of {symbol} "
        f"@ market (~${shares * reference_price:.2f} total)"
    )

    order_payload = {
        "combo_type": "NORMAL",
        "client_order_id": uuid.uuid4().hex,
        "symbol": symbol,
        "instrument_type": "EQUITY",
        "market": "US",
        "order_type": "MARKET",
        "quantity": str(shares),
        "support_trading_session": "CORE",
        "side": "BUY",
        "time_in_force": "DAY",
        "entrust_type": "QTY"
    }

    res = trade_client.order_v2.place_order(account_id, [order_payload])

    if res.status_code == 200:
        return res.json()
    else:
        print(f"Order failed ({res.status_code}): {res.text}")
        return None

# ==========================================
# TRADE EXECUTION WITH CONFIRMATION
# ==========================================


def show_chart(symbol, entry, stop, target):
    """
    Plots 6 months of daily OHLC data with EMAs, volume, entry/stop/target
    lines, and pauses until the user closes the window.
    """
    try:
        hist = yf.Ticker(symbol).history(period="6mo")

        if hist.empty:
            print(f"  (No chart data for {symbol})")
            return

        hist['20EMA'] = hist['Close'].ewm(span=20).mean()
        hist['50EMA'] = hist['Close'].ewm(span=50).mean()
        hist['200EMA'] = hist['Close'].ewm(span=200).mean()

        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(14, 8),
            gridspec_kw={'height_ratios': [3, 1]},
            sharex=True
        )
        fig.suptitle(f"{symbol}  |  Entry ${entry}  |  Stop ${stop}  |  Target ${target}",
                     fontsize=13, fontweight='bold', color='white')

        dates = hist.index
        closes = hist['Close']

        # --- Candlesticks (drawn as thin lines + body rectangles) ---
        for i, (date, row) in enumerate(hist.iterrows()):
            color = '#26a69a' if row['Close'] >= row['Open'] else '#ef5350'
            ax1.plot([i, i], [row['Low'], row['High']], color=color, linewidth=0.8)
            ax1.bar(i, abs(row['Close'] - row['Open']),
                    bottom=min(row['Open'], row['Close']),
                    color=color, width=0.6)

        x = list(range(len(hist)))

        ax1.plot(x, hist['20EMA'].values,  color='#f0c040', linewidth=1.2, label='20 EMA')
        ax1.plot(x, hist['50EMA'].values,  color='#4fc3f7', linewidth=1.2, label='50 EMA')
        ax1.plot(x, hist['200EMA'].values, color='#ce93d8', linewidth=1.2, label='200 EMA')

        # Entry / Stop / Target horizontal lines
        ax1.axhline(entry,  color='#00e676', linewidth=1.4, linestyle='--', label=f'Entry  ${entry}')
        ax1.axhline(stop,   color='#ff1744', linewidth=1.4, linestyle='--', label=f'Stop   ${stop}')
        ax1.axhline(target, color='#2979ff', linewidth=1.4, linestyle='--', label=f'Target ${target}')

        ax1.legend(loc='upper left', fontsize=8)
        ax1.set_ylabel('Price')
        ax1.set_facecolor('#1a1a2e')
        ax1.tick_params(colors='white')
        ax1.yaxis.label.set_color('white')
        fig.patch.set_facecolor('#1a1a2e')

        # --- Volume bars ---
        vol_colors = ['#26a69a' if hist['Close'].iloc[i] >= hist['Open'].iloc[i]
                      else '#ef5350' for i in range(len(hist))]
        ax2.bar(x, hist['Volume'].values, color=vol_colors, width=0.6)
        ax2.set_ylabel('Volume')
        ax2.set_facecolor('#1a1a2e')
        ax2.tick_params(colors='white')
        ax2.yaxis.label.set_color('white')

        # X-axis: show a date label every ~20 bars
        tick_positions = list(range(0, len(dates), max(1, len(dates) // 8)))
        ax1.set_xticks(tick_positions)
        ax2.set_xticks(tick_positions)
        ax2.set_xticklabels(
            [dates[i].strftime('%b %d') for i in tick_positions],
            rotation=30, ha='right', color='white'
        )

        plt.tight_layout()
        print(f"  [Chart open — close the window to continue]")
        plt.show()          # blocks until window is closed
        plt.close('all')

    except Exception as e:
        print(f"  (Chart error for {symbol}: {e})")


MAX_POSITIONS = 7


def get_account_summary(trade_client, account_id):
    """
    Returns (total_assets, cash_balance, open_position_count).
    total_assets  = total_net_liquidation_value or total_market_value
    cash_balance  = total_cash_balance (this is the buying power)
    """
    try:
        balance = trade_client.account_v2.get_account_balance(account_id).json()
        if "total_cash_balance" in balance:
            total_assets = float(balance.get("total_net_liquidation_value", 0) or 0)
            cash = float(balance.get("total_cash_balance", 0) or 0)
        else:
            total_assets = float(balance.get("total_market_value", 0) or 0)
            cash = total_assets
    except Exception:
        total_assets = 0.0
        cash = 0.0

    try:
        positions = trade_client.account_v2.get_account_position(account_id).json()
        open_count = len(positions) if positions else 0
    except Exception:
        open_count = 0

    return total_assets, cash, open_count


def get_buying_power(trade_client, account_id):
    """Fetches buying power — cash balance is the buying power."""
    _, cash, _ = get_account_summary(trade_client, account_id)
    return cash if cash > 0 else None


def confirm_and_execute_trades(trade_client, account_id, top_candidates):
    if top_candidates.empty:
        print("\nNo candidates passed the filters today. Nothing to trade.")
        return

    print("\n" + "=" * 60)
    print("TOP CANDIDATES SELECTED FOR REVIEW")
    print("=" * 60)
    print(top_candidates[
        ['Stock', 'Entry', 'Stop Loss', 'Target', 'Win Rate', 'Backtest Return']
    ].to_string(index=False))
    print("=" * 60)

    # ---- Equal-weight position sizing (max 7 total positions) ----
    total_assets, cash, open_count = get_account_summary(trade_client, account_id)
    num_candidates = len(top_candidates)
    remaining_slots = MAX_POSITIONS - open_count

    if remaining_slots <= 0:
        print(f"\nPortfolio is full ({open_count}/{MAX_POSITIONS} positions). No new trades.")
        return

    # Cap candidates to available slots
    if num_candidates > remaining_slots:
        print(f"\n{num_candidates} candidates but only {remaining_slots} slot(s) open — taking top {remaining_slots}.")
        top_candidates = top_candidates.head(remaining_slots)
        num_candidates = remaining_slots

    # Each slot gets an equal share of total assets divided by MAX_POSITIONS
    # so that if more positions come in later they stay balanced
    if total_assets > 0:
        slot_size = round(total_assets / MAX_POSITIONS, 2)
        # But never recommend more than available cash
        equal_slice = round(min(slot_size, cash / num_candidates), 2)
        print(
            f"\nPOSITION SIZING (max {MAX_POSITIONS} positions):"
            f"\n  Total Assets:      ${total_assets:,.2f}"
            f"\n  Cash (buying pwr): ${cash:,.2f}"
            f"\n  Open positions:    {open_count}/{MAX_POSITIONS}"
            f"\n  Slots available:   {remaining_slots}"
            f"\n  Per-slot size:     ${slot_size:,.2f}  (Total / {MAX_POSITIONS})"
            f"\n  Recommended/stock: ${equal_slice:,.2f}"
        )
    else:
        equal_slice = None
        print("\n(Could not fetch account data — no size recommendation available.)")
    print("=" * 60)
    # --------------------------------------

    for _, row in top_candidates.iterrows():
        symbol = row['Stock']
        entry = row['Entry']
        stop = row['Stop Loss']
        target = row['Target']
        win_rate = row['Win Rate']
        bt_return = row['Backtest Return']
        upside_pct = round((target - entry) / entry * 100, 1)

        print("\n" + "-" * 60)
        print(f"CANDIDATE: {symbol}")
        print(f"  Entry:             ${entry}")
        print(f"  Stop Loss:         ${stop}")
        print(f"  Target:            ${target}  (+{upside_pct}%)")
        print(f"  Win Rate:          {win_rate}%")
        print(f"  Backtest Return:   {bt_return}R")
        if equal_slice is not None:
            shares_estimate = math.floor(equal_slice / entry) if entry > 0 else "N/A"
            print(f"  Recommended Size:  ${equal_slice:,.2f}  (~{shares_estimate} shares)")
        print("-" * 60)

        # ---- Show chart ----
        show_chart(symbol, entry, stop, target)
        # --------------------

        confirm = input(f"Do you want to buy {symbol}? (y/n): ").strip().lower()
        if confirm != 'y':
            print(f"Skipping {symbol}.")
            continue

        order_type = 'MKT'
        limit_price = None

        # Pre-fill the recommended amount; let the user override it
        if equal_slice is not None:
            dollar_str = input(
                f"Dollar amount for {symbol} [recommended: ${equal_slice:,.2f}] "
                f"(press Enter to accept): "
            ).strip()
            dollar_amount = float(dollar_str) if dollar_str else equal_slice
        else:
            dollar_str = input(f"How many dollars to put into {symbol}?: ").strip()
            try:
                dollar_amount = float(dollar_str)
            except ValueError:
                print("Invalid dollar amount. Skipping.")
                continue

        try:
            result = place_buy_order(
                trade_client, account_id, symbol,
                dollar_amount, entry
            )
            print(f"Order response for {symbol}: {result}")
        except Exception as e:
            print(f"ERROR placing order for {symbol}: {e}")

# ==========================================
# MAIN
# ==========================================

def main():
    start = datetime.now()

    # 1. Scan
    df = run_scan(stocks)

    # 2. Filter to top candidates
    top_candidates = pick_top_candidates(df, max_picks=7)

    if top_candidates.empty:
        print("\nNo stocks met the BUY criteria "
              "(15%+ target, 80-100% win rate, >=5R backtest return).")
        print(f"\nCompleted in: {datetime.now() - start}")
        return

    # 3. Login — same pattern your test proved works
    print("\nLogging into Webull...")
    trade_client, account_id = webull_login()

    # 4. Show portfolio before trading
    show_portfolio(trade_client, account_id)

    # 5. Walk through candidates and execute with confirmation
    confirm_and_execute_trades(trade_client, account_id, top_candidates)

    # 6. Show updated portfolio after trading
    print("\nFetching updated portfolio...")
    show_portfolio(trade_client, account_id)

    print(f"\nCompleted in: {datetime.now() - start}")


if __name__ == "__main__":
    main()