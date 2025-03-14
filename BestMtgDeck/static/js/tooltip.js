// Set default rimg bbtag to 300
// Get all div elements with class "content"
// this code must run before adding event listeners
const contentDivs = document.querySelectorAll('div.content');

// Iterate over each div with class "content"
contentDivs.forEach(div => {
    // Get the inner HTML of the div
    let content = div.innerHTML;

    // Replace [rimg]...[/rimg] with <img> tags
    content = content.replace(/\[rimg\]([\s\S]*?)\[\/rimg\]/g, '<img src="$1" width="300" border="1">');

    // Set the modified content back to the div
    div.innerHTML = content;

    // Remove too many br tags before tables
    var tables = div.querySelectorAll('table');
    tables.forEach(table => {
        // Find all the <br> tags before the table
        var prevSibling = table.previousSibling;
        var granSibling = prevSibling ? prevSibling.previousSibling : null;
        while (prevSibling && granSibling && prevSibling.tagName === 'BR' && granSibling.tagName === 'BR') {
            if (granSibling.previousSibling && granSibling.previousSibling.tagName === 'BR') {
                granSibling.previousSibling.remove()
            } else {
                break
            }
        }
    })
});

function positionTooltip(tooltip, parent) {
    // ensure tooltip is below parent, even if weird legacy CSS would position it differently
    const parentRect = parent.getBoundingClientRect();

    // Calculate the left and top positions for the tooltip, taking scroll offset into account
    const top = parentRect.top + 5 + window.scrollY;

    // Apply the left and top positions to the tooltip
    tooltip.style.top = top + 'px';
}


function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (rect.right <= (window.innerWidth || document.documentElement.clientWidth));
}

function move(el) {
    if (!isElementInViewport(el)) {
        el.style.left = (window.innerWidth - el.offsetWidth * 1.5) + "px";
    }
}

const customCardsUrls = {
    'novellino': 'https://i.imgur.com/G4RvYzu.jpeg',
    'neomoderatore': 'https://i.imgur.com/RXURlk7.jpeg',
    'aspirante mod': 'https://i.imgur.com/js01WJQ.jpeg',
    'moderatore dai commenti costruttivi': 'https://i.imgur.com/t3qKDZk.jpeg',
    'trapper': 'https://i.imgur.com/uMJdSMI.jpeg',
    'appassionato del forum': 'https://i.imgur.com/yIbDMeG.jpeg',
    'seguace dei trapper': 'https://i.imgur.com/gazNdbt.jpeg',
    'utente valoroso': 'https://i.imgur.com/ACvIHr2.png',
    'pagina del regolamento': 'https://i.imgur.com/rTFhAjR.jpeg',
    'mod amato dalla folla': 'https://i.imgur.com/tsVdXwa.jpeg',
    'ravvivare la conversazione': 'https://i.imgur.com/xrZy2fP.jpeg',
    "questa è l'ultima infrazione": 'https://i.imgur.com/Lpk6Q77.jpeg',
    'permesso speciale': 'https://i.imgur.com/4r8tODO.jpeg',
    'verdetto del popolino': 'https://i.imgur.com/irgePDG.jpeg',
    'armonia tra gli utenti': 'https://i.imgur.com/pEVwIVY.jpeg',
    'aggiorno la lista': 'https://i.imgur.com/RiQuJ0H.jpeg',
    "restrizioni all'account": 'https://i.imgur.com/xruyr11.jpeg',
    'cricca di amici': 'https://i.imgur.com/zEFat8K.png',
    'pecorone trascinato': 'https://i.imgur.com/1SEXxAB.jpeg',
    'alvoi, guardiano del forum': 'https://i.imgur.com/pJxrAgu.png',
    'mikefon, commentatore saggio': 'https://i.imgur.com/V1gvg6g.jpeg',
    'utente pecorone': 'https://i.imgur.com/3fhh5Q7.jpeg',
    'groupie forgiatrice': 'https://i.imgur.com/x3X1wUl.jpeg',
    'pimpatore squattrinato': 'https://i.imgur.com/Anl6w5s.png',
    'pulizia dei contenuti': 'https://i.imgur.com/0XAQ0zX.jpeg',
    "solidarietà dell'utenza": 'https://i.imgur.com/MVbsQFz.jpeg',
    'riaprire il dibattito': 'https://i.imgur.com/z4Z3biO.jpeg',
    'la storia di alvoi': 'https://i.imgur.com/YjvdD93.jpeg',
    'goharoth, il co-fondatore': 'https://i.imgur.com/WcMrGp4.jpeg',
    'protettore della home': 'https://i.imgur.com/MYaP5Ly.jpeg',
    'pimpatrice facoltosa': 'https://i.imgur.com/m5hioJO.jpeg',
    'censore di diablo': 'https://i.imgur.com/ITxsyuM.png',
    'moderatore stizzito': 'https://i.imgur.com/fB20sZB.jpeg',
    "non capisco quest'astio...": 'https://i.imgur.com/wYD8JAs.jpeg',
    'lista da commander': 'https://i.imgur.com/OF8WFA8.jpeg',
    'difesa del forum di alvoi': 'https://i.imgur.com/8VyNAdL.jpeg',
    "exlo, maestro dell'artificio": 'https://i.imgur.com/3nNfX2l.jpeg',
    "apocalisse dell'amministrazione": 'https://i.imgur.com/UnCIJux.jpeg',
    'recisore di link': 'https://i.imgur.com/2AiWReR.png',
    'spione': 'https://i.imgur.com/bnh948B.png',
    'utente visionario': 'https://i.imgur.com/RclOtSE.jpeg',
    'creatore di fantacarte': 'https://i.imgur.com/bvLgw3i.jpeg',
    'trafugatore di dati': 'https://i.imgur.com/08o1zcp.jpeg',
    'topic di speculazione': 'https://i.imgur.com/qXNfPE2.jpeg',
    'moderatore paranoide': 'https://i.imgur.com/VHc4vQm.jpeg',
    'aspirante truffaldino': 'https://i.imgur.com/OQpCeXr.jpeg',
    'topic di news': 'https://i.imgur.com/nvIBM1X.png',
    'bot rivelatore': 'https://i.imgur.com/HZ9e3ti.jpeg',
    'limite di caratteri': 'https://i.imgur.com/EGTURhP.png',
    'restrizione temporanea': 'https://i.imgur.com/RsVE70X.png',
    'funzione cerca': 'https://i.imgur.com/DGUxFVx.jpeg',
    'funzione di aiuto': 'https://i.imgur.com/a2aD5jN.png',
    'verificare le fonti': 'https://i.imgur.com/SZU1bTE.jpeg',
    'guardare la card gallery': 'https://i.imgur.com/JDgfqGR.png',
    'mucho texto': 'https://i.imgur.com/CtCyw51.jpeg',
    'incursore rubadati': 'https://i.imgur.com/YsVrNyp.png',
    'planeswalker97': 'https://i.imgur.com/HhNdDJ1.png',
    'seppia di alvoi': 'https://i.imgur.com/1oKCvNC.png',
    'topic di ristampe': 'https://i.imgur.com/XcWoRZK.png',
    'leonhard degli svaghi': 'https://i.imgur.com/msBbWZ3.png',
    'bot spoileratore': 'https://i.imgur.com/hkr8Ce0.jpeg',
    'paninizzazione': 'https://i.imgur.com/XSQyyHS.png',
    'messaggio di warning': 'https://i.imgur.com/ucOHekT.png',
    'monopolizzare la discussione': 'https://i.imgur.com/z4kMbnH.png',
    'arabic crea bestdeck4u': 'https://i.imgur.com/I82upMO.jpeg',
    'controllo del traffico dati': 'https://i.imgur.com/NVtR0bK.png',
    'leviatano, utente dal profondo': 'https://i.imgur.com/cHEt1bk.jpeg',
    'mago lanciosvelto': 'https://i.imgur.com/udpsQ7R.jpeg',
    'programmatore di bot': 'https://i.imgur.com/032Zvw3.png',
    'doppio post': 'https://i.imgur.com/44JTtVc.jpeg',
    'mod con tempo libero': 'https://i.imgur.com/tLotVew.jpeg',
    'worm': 'https://i.imgur.com/gtThKDQ.jpeg',
    'caricamento di spoiler massivo': 'https://i.imgur.com/YFj1AFI.jpeg',
    'impersonamento di massa': 'https://i.imgur.com/R3Tlm33.png',
    'khalni, idrago mutevole': 'https://i.imgur.com/RnbQ7vB.jpeg',
    'raptus di nuovi post': 'https://i.imgur.com/cq7LKHy.png',
    'aspirante spocchioso': 'https://i.imgur.com/34tgmLQ.jpeg',
    "troll dell'ultima parola": 'https://i.imgur.com/Dlcs4N6.jpeg',
    'nuovo utente sospetto': 'https://i.imgur.com/3hbpyVC.png',
    'bot chiacchierone': 'https://i.imgur.com/awvWNr9.jpeg',
    'cercatore di necropost': 'https://i.imgur.com/NvaGb9U.png',
    'troll fastidioso': 'https://i.imgur.com/t2CVN0j.jpeg',
    'dispensatore di leak falsi': 'https://i.imgur.com/MgCT0LP.jpeg',
    'novellino snob': 'https://i.imgur.com/JEUC9p6.png',
    'rimangiatore di spoiler': 'https://i.imgur.com/lPOv2rR.jpeg',
    'account riattivato': 'https://i.imgur.com/6CJY8h2.jpeg',
    'lurker dei tempi andati': 'https://i.imgur.com/75vHji6.jpeg',
    'tagliare la connessione': 'https://i.imgur.com/b7InO5K.png',
    'ultimo commento': 'https://i.imgur.com/zThEGUA.jpeg',
    'ho cliccato il link!': 'https://i.imgur.com/TMpRsxZ.jpeg',
    'ritorno di flamma': 'https://i.imgur.com/dV6OcQr.jpeg',
    'trascinare nel ban': 'https://i.imgur.com/RNZQVJg.jpeg',
    "mi sono perso l'ultimo spoiler!": 'https://i.imgur.com/1QdEeJT.jpeg',
    "bru, l'ombra persistente": 'https://i.imgur.com/Yw9W08S.jpeg',
    'torta di goblin': 'https://i.imgur.com/FARn3qh.jpeg',
    'divorautenti': 'https://i.imgur.com/jVcBb1L.jpeg',
    'troll istigatore': 'https://i.imgur.com/O7eTVIk.jpeg',
    'ro-bot-tone': 'https://i.imgur.com/bvt1gft.jpeg',
    'venditore di passaporti falsi': 'https://i.imgur.com/Daw5mXt.jpeg',
    'leak clandestino': 'https://i.imgur.com/JnPsMMM.jpeg',
    'riesumare le credenziali': 'https://i.imgur.com/zbglja0.png',
    'tradire gli ideali del forum': 'https://i.imgur.com/pwiELWT.jpeg',
    'commento ingenuo': 'https://i.imgur.com/3LM8Gk0.jpeg',
    'la caduta di diablo': 'https://i.imgur.com/ugTED7k.jpeg',
    'ciciarampa, colui che è': 'https://i.imgur.com/DcTm8mi.jpeg',
    'giocatore di rockanimator': 'https://i.imgur.com/AETkGDa.jpeg',
    'ladro di spoiler sheet': 'https://i.imgur.com/4mDoEbT.jpeg',
    'troll mutevole': 'https://i.imgur.com/YFlyTjl.jpeg',
    'spettro della sottosezione': 'https://i.imgur.com/HrSz3yK.jpeg',
    'malconsigliare gli utenti': 'https://i.imgur.com/SVI1HNq.jpeg',
    'truffatore inesorabile': 'https://i.imgur.com/mK9gwMt.jpeg',
    'regime di terrore': 'https://i.imgur.com/cR81DC0.jpeg',
    "sorin marco, l'arcimago": 'https://i.imgur.com/rC4PxwM.jpeg',
    'llama del fato': 'https://i.imgur.com/QJjdiTj.jpeg',
    'trollatog': 'https://i.imgur.com/PII9KDt.jpeg',
    'troll masochista': 'https://i.imgur.com/knWlErs.jpeg',
    'fan dei draghi': 'https://i.imgur.com/BPZ0jWI.jpeg',
    'appassionato del mazzo maghi': 'https://i.imgur.com/CIMjYHg.jpeg',
    'aspirante flamer': 'https://i.imgur.com/lVsATLR.jpeg',
    'troll flammante': 'https://i.imgur.com/uEjrecI.jpeg',
    'discorso off topic': 'https://i.imgur.com/NM9cao9.jpeg',
    'area dei fantaset': 'https://i.imgur.com/PixXthJ.jpeg',
    'storico utente gregario': 'https://i.imgur.com/RZYvBNW.jpeg',
    'ritrovo di vecchi utenti': 'https://i.imgur.com/cPVi7pQ.jpeg',
    'risposta piccata': 'https://i.imgur.com/oGmBpxk.jpeg',
    "rabbia dell'utenza": 'https://i.imgur.com/zi6aVKK.jpeg',
    'editare furiosamente il post': 'https://i.imgur.com/9a4L7rD.jpeg',
    'passare al flame': 'https://i.imgur.com/xvp4WvJ.jpeg',
    'risposta furente': 'https://i.imgur.com/255V87C.jpeg',
    'raduno di flamer': 'https://i.imgur.com/BPSY8j8.jpeg',
    'spam maniacale': 'https://i.imgur.com/rxAgOgO.jpeg',
    'pochy, commentatore estroso': 'https://i.imgur.com/V0tuBhu.jpeg',
    'troll analfabeta': 'https://i.imgur.com/kuLQwic.jpeg',
    'sostenitore infervorato': 'https://i.imgur.com/bXefbxE.jpeg',
    'magicitek, deckbuilder estremo': 'https://i.imgur.com/fJVcIBA.jpeg',
    'trollone': 'https://i.imgur.com/DSJ1cZL.jpeg',
    'dragobot': 'https://i.imgur.com/Mv8trrU.jpeg',
    'discussioni caustiche': 'https://i.imgur.com/4QCZtCZ.jpeg',
    'sclerata epocale di emilio': 'https://i.imgur.com/v9UQ8kW.jpeg',
    'parte il pippozzo': 'https://i.imgur.com/KoCpn4d.jpeg',
    'trollata generale': 'https://i.imgur.com/RsmNDKX.jpeg',
    'junius riassume le storie': 'https://i.imgur.com/kRjZygE.jpeg',
    'monopro, mai domato': 'https://i.imgur.com/3I9eUlT.jpeg',
    'thread di speculazioni': 'https://i.imgur.com/8VQxlKk.jpeg',
    'giocatore infervorato': 'https://i.imgur.com/akIj5UF.jpeg',
    'draco volante in fuga': 'https://i.imgur.com/DjeVcny.jpeg',
    'frecciatina fastidiosa': 'https://i.imgur.com/p45xJnZ.jpeg',
    'creazione di 8-kor di junius': 'https://i.imgur.com/DPKMI2m.jpeg',
    'risposte roventi di fillo': 'https://i.imgur.com/8DXBncM.jpeg',
    'infestazione trollosa': 'https://i.imgur.com/wsbsijz.jpeg',
    'tgbof, sovrano delle fiamme': 'https://i.imgur.com/AZ6e162.jpeg',
    'la grande palla di fuoco': 'https://i.imgur.com/RIs8SpL.jpeg',
    'organizzatore di tornei amatoriali': 'https://i.imgur.com/LAlbYZu.jpeg',
    'aspirante utente storico': 'https://i.imgur.com/R6Hr94B.jpeg',
    'conversatore partecipe': 'https://i.imgur.com/OVVgQKj.jpeg',
    'articolista della home': 'https://i.imgur.com/Il8PEzs.jpeg',
    'araldo di hamza': 'https://i.imgur.com/Lw7Xhwx.jpeg',
    'seguace di utenti famosi': 'https://i.imgur.com/BfgYzgf.jpeg',
    'utente prolifico': 'https://i.imgur.com/RtrTgfM.jpeg',
    'esperto utente pacato': 'https://i.imgur.com/ZJK8FqS.jpeg',
    'novellino ignorato': 'https://i.imgur.com/sTG22Yv.jpeg',
    'utente giurassico': 'https://i.imgur.com/PVxw2CY.jpeg',
    'gran conoscitore di carte': 'https://i.imgur.com/8pMfVk9.jpeg',
    'antico utente dimenticato': 'https://i.imgur.com/PiFXMRT.jpeg',
    'risposta ben scritta': 'https://i.imgur.com/b8jgibp.jpeg',
    'riordinare la sezione': 'https://i.imgur.com/NghqyGk.jpeg',
    'zittire il troll': 'https://i.imgur.com/2QllUsz.jpeg',
    'riorganizzare le discussioni': 'https://i.imgur.com/1chApVM.jpeg',
    'rimarcare': 'https://i.imgur.com/ld2IJS9.jpeg',
    'camilla salander, gatta guerriera': 'https://i.imgur.com/VEDMD1C.jpeg',
    'ristampa insistente': 'https://i.imgur.com/YPegE6H.jpeg',
    'utente quasistorico': 'https://i.imgur.com/BTpbFr8.jpeg',
    'e la rana': 'https://i.imgur.com/asrxlFX.jpeg',
    'veteraptor bellicoso': 'https://i.imgur.com/A7762l8.jpeg',
    'aggiornaliste di hamza': 'https://i.imgur.com/UvturxQ.jpeg',
    'gostan il collezionista': 'https://i.imgur.com/ajaVQ6J.jpeg',
    'la vendetta di linneo': 'https://i.imgur.com/1aHXPmE.jpeg',
    'nuovo benvenuto': 'https://i.imgur.com/aJdmAYc.jpeg',
    'raduno a zenevredo': 'https://i.imgur.com/AggsqAZ.jpeg',
    'eterna spoiler season': 'https://i.imgur.com/XWHkIFf.jpeg',
    'howardroark, giocatore di forza': 'https://i.imgur.com/qjoZh3t.jpeg',
    'necrocommanderista': 'https://i.imgur.com/oSdSLrE.jpeg',
    'navigatore cercadiscussioni': 'https://i.imgur.com/6vOSndN.jpeg',
    'masticatore di vecchi thread': 'https://i.imgur.com/OvZBDIO.jpeg',
    'commentatore instancabile': 'https://i.imgur.com/NCpeAcd.jpeg',
    'gyed, cronistorico': 'https://i.imgur.com/8G3lGNu.jpeg',
    'carica degli utenti anziani': 'https://i.imgur.com/3gERrR0.jpeg',
    'discussioni germoglianti': 'https://i.imgur.com/VqemV2V.jpeg',
    'the swarmer, ombra strisciante': 'https://i.imgur.com/i0dgkad.jpeg',
    'trio di hamza': 'https://i.imgur.com/SjgtfYy.jpeg',
    'vexac, gestore di utenti': 'https://i.imgur.com/ZyQshM4.jpeg',
    'bottlegnome': 'https://i.imgur.com/HfMpBui.jpeg',
    'mr. koth il furente': 'https://i.imgur.com/WeZCfMb.jpeg',
    'max game, giocatore amichevole': 'https://i.imgur.com/KEtbRJy.jpeg',
    'mr b, prophet of hamza': 'https://i.imgur.com/EbKR9nM.jpeg',
    'tulio jabba, dibattente pristino': 'https://i.imgur.com/BIV0pcC.jpeg',
    'valto il ritornato': 'https://i.imgur.com/iEKNSoj.jpeg',
    'cemento, degustatore simic': 'https://i.imgur.com/KE0n0Jc.png',
    'fabrimagic, inventore partecipe': 'https://i.imgur.com/2aKB3Bp.jpeg',
    'fillo, templare infervorante': 'https://i.imgur.com/bfSu75r.jpeg',
    'loa, moderatore sottomarino': 'https://i.imgur.com/l0o2gwG.jpeg',
    'mikokorigames, seminatore di discordia': 'https://i.imgur.com/stThmGv.jpeg',
    'riot, spadellatore impetuoso': 'https://i.imgur.com/8eV0Vqd.jpeg',
    'erzinston, commanderista atipico': 'https://i.imgur.com/Cy55xhE.png',
    "l'accogliente donchi": 'https://i.imgur.com/Woib7yn.jpeg',
    'umbert710, il lockatore': 'https://i.imgur.com/c0zT7IT.jpeg',
    'dario18, sconquassaformati': 'https://i.imgur.com/xRp0iuz.jpeg',
    "jtk88, torneista all'apice": 'https://i.imgur.com/EjFTJsY.jpeg',
    'magicmax, creatore di concorsi': 'https://i.imgur.com/RwIDhSa.jpeg',
    'tarox, forgiatore di luce': 'https://i.imgur.com/bJps8Qp.jpeg',
    'sting, fuori dagli schemi': 'https://i.imgur.com/zICjChs.png',
    'ciotola, che aspetta consigli': 'https://i.imgur.com/rF2am0D.jpeg',
    'attila lo scuoia capre': 'https://i.imgur.com/iiDK7Qc.jpeg',
    'darigaaz83, commanderista fiammante': 'https://i.imgur.com/xqFFP27.jpeg',
    'steelstar, esperto di limited': 'https://i.imgur.com/uxzLdMh.jpeg',
    'al pharazon, flagello di pikula': 'https://i.imgur.com/OR81w3M.jpeg',
    'deugemo, che guarda ad est': 'https://i.imgur.com/Hq7uMnf.jpeg',
    'rancore, evolved designer': 'https://i.imgur.com/HvY1rMD.jpeg',
    'kyogre, forza primordiale': 'https://i.imgur.com/ShKF6wg.png',
    'junius halsey, amante': 'https://i.imgur.com/4vGu4y2.jpeg',
    'arabiclawrence, mastro programmatore': 'https://i.imgur.com/09HIet2.jpeg',
    'diablo': 'https://i.imgur.com/DhteFzW.jpeg',
    'gosh83, the paninator': 'https://i.imgur.com/9dRDwFk.jpeg',
    'legolax, campione jund': 'https://i.imgur.com/aFvuzx3.jpeg',
    'emilio, sovrano della megafauna': 'https://i.imgur.com/YY6QBi2.jpeg',
    'alex, il creatore': 'https://i.imgur.com/mzNzFci.png',
    'alex crea il forum': 'https://i.imgur.com/uimXQcz.jpeg',
    "gestore dell'archivio": 'https://i.imgur.com/BVvWFPY.jpeg',
    'pulsante "nuova discussione"': 'https://i.imgur.com/L1DJwlZ.jpeg',
    'usurpatore di account': 'https://i.imgur.com/TaIoZ2X.jpeg',
    'utente qualunquista': 'https://i.imgur.com/9SAbUvm.jpeg',
    'server surriscaldato': 'https://i.imgur.com/ZZ0EjAa.jpeg',
    'interfaccia migliorata': 'https://i.imgur.com/C6GIxOi.jpeg',
    'kebab di hamza': 'https://i.imgur.com/4TrkqlY.jpeg',
    'chiave privata': 'https://i.imgur.com/2qNagNG.jpeg',
    'invasione di bot': 'https://i.imgur.com/kRgCHGF.jpeg',
    'argomento vivente': 'https://i.imgur.com/Wv0Utbc.jpeg',
    'uomocomune, modellatore di carte': 'https://i.imgur.com/UeyMoEP.jpeg',
    'banhammer': 'https://i.imgur.com/oxeDfKd.jpeg',
    'aereo per la colombia': 'https://i.imgur.com/t9J2CNk.jpeg',
    'metamox': 'https://i.imgur.com/8WWsqyt.jpeg',
    'la fenice di metagame': 'https://i.imgur.com/rAF5kvQ.jpeg',
    'discussione placida': 'https://i.imgur.com/vvOvjSX.jpeg',
    'discussione infiltrata': 'https://i.imgur.com/Smqjjs9.jpeg',
    'discussione flammante': 'https://i.imgur.com/b3Ib38w.jpeg',
    'discussione storica': 'https://i.imgur.com/riitSIb.jpeg',
    'discussione armonica': 'https://i.imgur.com/Q0SFZ91.jpeg',
    'discussione monotematica': 'https://i.imgur.com/iMmcFev.png',
    'discussione stravagante': 'https://i.imgur.com/wjSOefB.jpeg',
    'discussione datata': 'https://i.imgur.com/xK3dFLB.jpeg',
    'discussione costruttiva': 'https://i.imgur.com/N1N9Elx.jpeg',
    'discussione divulgativa': 'https://i.imgur.com/ShzVSOT.jpeg',
    'database degli utenti': 'https://i.imgur.com/8AC4YAP.jpeg',
    '"regolamento generale"': 'https://i.imgur.com/aD4fXrR.png',
    '"speculazioni sulle possibili prossime espansioni"': 'https://i.imgur.com/a3WaMwa.jpeg',
    '"dead guy ale"': 'https://i.imgur.com/6AbQJoX.jpeg',
    '"crea la tua carta anarchico"': 'https://i.imgur.com/bXhMxG4.jpeg',
    '"ciao a tutti!"': 'https://i.imgur.com/BXCZKnM.jpeg',
    '"angolo del pimp"': 'https://i.imgur.com/RCAlA4s.jpeg',
    '"golden topic citazioni"': 'https://i.imgur.com/XmxKLYF.jpeg',
    '"metagame il fantaset del forum"': 'https://i.imgur.com/RpZfAV0.jpeg'
}

function createTooltip(target_link, cardName, storeLink, prices_cache, event) {
    let tooltip_div = target_link.querySelector('a');
    let text;

    if (!tooltip_div) {
        tooltip_div = document.createElement('a')
        tooltip_div.href = storeLink;
        tooltip_div.target = "_blank";
        tooltip_div.classList.add('cardtrader_i_tooltip', 'image');

        const img = document.createElement('img');
        text = document.createElement('p');

        cardName = cardName.toLowerCase()
        if (cardName in customCardsUrls) {
            img.src = tooltip_div.href = customCardsUrls[cardName]
        } else {
            img.src = tooltip_div.href = "https://api.cardtrader.com/api/metagame_it/v1/magic/" + cardName + '/image';
        }
        let imgLink = document.createElement('a');
        imgLink.href = storeLink;
        imgLink.target = "_blank";
        imgLink.appendChild(img);

        tooltip_div.appendChild(imgLink);
        tooltip_div.appendChild(text);
        target_link.appendChild(tooltip_div);
    } else {
        text = target_link.querySelector('p');
    }

    if ((cardName in prices_cache) && (text.textContent !== "Loading...")) {
        text.textContent = "A partire da: " + prices_cache[cardName] + " €";
    } else {
        text.textContent = "Loading...";
        fetch("https://api.cardtrader.com/api/metagame_it/v1/magic/" + cardName + "/info")
            .then(response => response.json())
            .then(response => {
                text.textContent = "A partire da: " + response.price + " €";
                prices_cache[cardName] = response.price;
            })
    }
    positionTooltip(tooltip_div, target_link);
    move(tooltip_div);
}

// detect if touch device
const touchDevice = (('ontouchstart' in window) || (navigator.maxTouchPoints > 0));

// convert broken [card] tags to links
const postBodies = document.querySelectorAll('.postbody');
postBodies.forEach(postBody => {
    let replaceValue;
    if (touchDevice) {
        replaceValue = '<a class="CardTraderTooltip">$1</a>';
    } else {
        replaceValue = '<a href="https://api.cardtrader.com/api/metagame_it/v1/magic/$1/shop" class="CardTraderTooltip" target="_blank">$1</a>';
    }
    postBody.innerHTML = postBody.innerHTML.replace(/\[card\](.*?)\[\/card\]/gi, replaceValue);
});

// select links to cards
const links = document.querySelectorAll("a.DeckTutorCard, a.CardTraderTooltip, a[href^='https://deckbox.org/mtg/'], a[href^='http://ws.decktutor.com/tooltip']");
let prices = {};  // cache for prices

links.forEach(link => {
    // remove the back face from double faced cards
    const cardName = link.textContent.trim().split(" /", 1)[0];
    const storeLink = "https://api.cardtrader.com/api/metagame_it/v1/magic/" + cardName + "/shop";
    if (touchDevice) {
        link.href = "#void";
        link.removeAttribute('target');
    } else {
        // correct hyperlinks if wrong (old posts or double faced cards)
        if (link.href !== storeLink) {
            link.href = storeLink;
            link.target = "_blank";
        }
    }
    link.addEventListener('mouseover', (event) => createTooltip(link, cardName, storeLink, prices, event));
    link.addEventListener('pointerdown', (event) => {
        createTooltip(link, cardName, storeLink, prices, event);
        if (event.pointerType === "touch" && event.target === link) {
            event.preventDefault();
            let tooltip = link.querySelector('.cardtrader_i_tooltip');
            let tooltips = document.querySelectorAll('.cardtrader_i_tooltip');
            if (tooltip.style.visibility === 'visible') {
                tooltips.forEach(tooltip => tooltip.style.visibility = 'hidden');
            } else {
                tooltips.forEach(tooltip => tooltip.style.visibility = 'hidden');
                tooltip.style.visibility = 'visible';
            }
        }
    });
});


const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = 'https://bestdeckforyou.pythonanywhere.com/static/css/tooltip.css';
document.head.appendChild(link);