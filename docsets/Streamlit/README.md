Streamlit Dash Docset
=======================

## Info


[Streamlit](https://streamlit.io/) docset for Dash, created by [WangX](https://github.com/WangX0111). 


## Docset Generation

Run dash mac app
1. Select "Download Websit"
2. Website url: https://docs.streamlit.io/develop/api-reference, download page matching: https://docs.streamlit.io/develop/api-reference/*
3. Dockset nam: "Streamlit"
4. Select "Custom index"
5. javascript:
```javascript
function updateColors() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.style.backgroundColor = 'black';
        document.body.style.color = 'white';
    } else {
        document.body.style.backgroundColor = 'white';
        document.body.style.color = 'black';
    }
}

updateColors();

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateColors);
window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', updateColors);

const pageTitle = $("title").text();
dashDoc.addEntry({name: pageTitle, type: "Guide"});

// remove Cookie 
$(".gdpr_Container__MXNt0").remove();
$("header").remove();
// $("body").css("background-color", "normal");

const sections = $("section.autofunction_Container__FYLCH");

$(".autofunction_Container__FYLCH").each(function() {
    const entryName = $(this).text();
    var entryHash = $(this).attr('id');
    if(!entryHash)
    {
        entryHash = entryName.replace(/\W/g, '');
        $(this).attr('id', entryHash);
    }
    dashDoc.addEntry({name: entryName, type: "Section", hash: entryHash});
});
```
6. css
```css
footer {
    display: none !important;
}
body {
    background-color: normal !important;
    color: normal;
}
```
7. done