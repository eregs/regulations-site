function makeStateful(el) {
    const state_change_target = el.getAttribute("data-state-name");
    const state_change_buttons = document.querySelectorAll(`[data-set-state][data-state-name='${state_change_target}']`);

    for (const state_change_button of state_change_buttons) {
        state_change_button.addEventListener('click', function() {
            el.setAttribute("data-state", this.getAttribute("data-set-state"));
        });
    }
}

function goToVersion() {
    const select = document.querySelector("#view-options");
    const options = document.querySelectorAll("#view-options [data-url]");

    select.addEventListener('change', function() {
        location.href  = this.options[this.selectedIndex].dataset.url;
    });

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

