function makeStateful(el) {
    const state_change_target = el.getAttribute("data-state-name");
    const state_change_buttons = document.querySelectorAll(`[data-set-state][data-state-name='${state_change_target}']`);

    for (const state_change_button of state_change_buttons) {
        state_change_button.addEventListener('click', function() {
            const state = this.getAttribute("data-set-state");
            el.setAttribute("data-state", state);
        });
    }
}

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

function main() {
    const stateful_elements = document.querySelectorAll("[data-state]")

    for (const el of stateful_elements) {
        makeStateful(el);
    }

}

main();
goToVersion();

