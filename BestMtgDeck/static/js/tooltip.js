function positionTooltip(tooltip, parent) {
    // ensure tooltip is below parent, even if weird legacy CSS would position it differently
    const parentRect = parent.getBoundingClientRect();
    // const tooltipRect = tooltip.getBoundingClientRect();

    // Calculate the left and top positions for the tooltip, taking scroll offset into account
    // const left = parentRect.left + parentRect.width + 5 + window.scrollX;
    const top = parentRect.top + 5 + window.scrollY;

    // Apply the left and top positions to the tooltip
    // tooltip.style.position = 'absolute';
    // tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}


function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        // rect.top >= 0 &&
        // rect.left >= 0 &&
        // rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

function move(el) {
    if (!isElementInViewport(el)) {
        el.style.left = (window.innerWidth - el.offsetWidth * 1.5) + "px";
    }
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

        img.src = tooltip_div.href = "https://www.cardtrader.com/api/metagame_it/v1/magic/" + cardName + '/image';
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
        fetch("https://www.cardtrader.com/api/metagame_it/v1/magic/" +
            cardName + "/info")
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
        replaceValue = '<a href="https://www.cardtrader.com/api/metagame_it/v1/magic/$1/shop" class="CardTraderTooltip" target="_blank">$1</a>';
    }
    postBody.innerHTML = postBody.innerHTML.replace(/\[card\](.*?)\[\/card\]/gi,
        replaceValue);
});

// select links to cards
const links = document.querySelectorAll("a.DeckTutorCard, a.CardTraderTooltip, a[href^='https://deckbox.org/mtg/'], a[href^='http://ws.decktutor.com/tooltip']");
let prices = {};  // cache for prices

links.forEach(link => {
        // remove the back face from double faced cards
        const cardName = link.textContent.trim().split(" /", 1)[0];
        const storeLink = "https://www.cardtrader.com/api/metagame_it/v1/magic/" + cardName + "/shop";
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
    }
);


const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = 'https://bestdeckforyou.pythonanywhere.com/static/css/tooltip.css';
document.head.appendChild(link);