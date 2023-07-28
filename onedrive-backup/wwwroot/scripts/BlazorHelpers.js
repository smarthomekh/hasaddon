﻿var blazorPassThrough = false;

function addTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}

function copyToClipboard(txt) {
    navigator.clipboard.writeText(txt);
}

function showAlert(title, message, type, linkUrl, linkCaption, message2) {
    const alertPlaceholder = document.getElementById('alertPlaceholder');
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
        `<div class="alert alert-${type}" role="alert">`,
        `   <div><strong>${title}</strong>${message}<a href="${linkUrl}" class="alert-link">${linkCaption}</a>${message2}</div>`,
        '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)
}

function checkBlazorStatus() {
    var markup = document.documentElement.innerHTML;
    if (markup.includes("<!--Blazor") == false) {
        blazorPassThrough = true;
        showAlert("Error! ", "Html Content Filtering Detected - Web Interface will not work. If you are using Cloudflare or a similar service please follow", "danger", "https://github.com/lavinir/hassio-onedrive-backup#html-content-filtering-error", " this link ", "for instructions");
    }
}

window.onload = function () {
    checkBlazorStatus();
}