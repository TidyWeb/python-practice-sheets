/* Python Practice Sheets: shared rail behaviour.
   1. On small screens the route and hints fold away behind two buttons, so the exercise comes first.
   2. Clicking the barrier lifts the arm before going to the car park. */
(function () {
  var rail = document.querySelector(".rail");
  if (!rail) return;
  rail.classList.add("js-rail");

  rail.querySelectorAll(".rail-toggles button").forEach(function (button) {
    var panel = document.getElementById(button.getAttribute("aria-controls"));
    if (!panel) return;
    button.addEventListener("click", function () {
      var open = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", open ? "true" : "false");
      panel.classList.toggle("is-open", open);
    });
  });

  document.addEventListener("click", function (event) {
    var link = event.target.closest(".route-barrier");
    if (!link || link.classList.contains("is-open")) return;
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    event.preventDefault();
    link.classList.add("is-opening");
    window.setTimeout(function () { window.location.href = link.href; }, 1850);
  });
})();
