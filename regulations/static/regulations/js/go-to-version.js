function goToVersion() {
    const select = document.querySelector("#view-options");
    const options = document.querySelectorAll("#view-options [data-url]");

    select.addEventListener('change', function() {
        location.href  = this.options[this.selectedIndex].dataset.url;
    });

    // if not latest version show view div
    const latest_version = options[0].dataset.url;

    if(!location.href.includes(latest_version)) {
        const state_change_target = "view"
        const view_elements = document.querySelectorAll(`[data-state][data-state-name='${state_change_target}']`);
        for (const el of view_elements) {
          el.setAttribute("data-state", "show");
        }
    }

    for(const option of options) {
        const url = option.dataset.url;
        if(location.href.includes(url)) {
            option.setAttribute("selected", "");
            break;
        }
    }
}

goToVersion();
