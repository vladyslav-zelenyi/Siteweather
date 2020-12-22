$(document).ready(function () {
  $("#previous_page").click(function (event) {
    event.preventDefault();
    location.href = document.referrer;
  })
})
