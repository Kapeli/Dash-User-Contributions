var ToC =
  "<nav role='navigation' class='table-of-contents'>" +
    "<h2>On this page:</h2>" +
    "<ul>";

var newLine, el, title, link;
console.log($("h1"))

$( document ).ready(function() {

$("h1").each(function() {

  el = $(this);
  title = el.text();
  anchor = $(this).next();
  link = "#" + anchor.attr("name");

  newLine =
    "<li>" +
      "<a href='" + link + "'>" +
        title +
      "</a>" +
    "</li>";

  ToC += newLine;

});

ToC +=
   "</ul>" +
  "</nav>";

$(".all-questions").prepend(ToC);});
