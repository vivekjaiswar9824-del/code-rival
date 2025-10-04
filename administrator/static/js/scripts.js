document.addEventListener("DOMContentLoaded", function () {
    const testBtn = document.getElementById("testButton");
    if (testBtn) {
        testBtn.addEventListener("click", () => {
            alert("JS is working!");
        });
    }
});


// Hide loader after page load
window.addEventListener("load", function () {
  const loaderWrapper = document.getElementById("loader-wrapper");
  if (loaderWrapper) {
    loaderWrapper.style.opacity = 0;
    setTimeout(() => loaderWrapper.style.display = "none", 500);
  }
});



