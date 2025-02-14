document.addEventListener("DOMContentLoaded", function () {
    const fileInputs = document.querySelectorAll("input[type='file']");
    
    fileInputs.forEach(input => {
        input.addEventListener("change", function () {
            if (this.files.length > 0) {
                alert("File selected: " + this.files[0].name);
            }
        });
    });
});
