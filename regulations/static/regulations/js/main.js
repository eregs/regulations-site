function makeStateful(el) {
    const state_change_buttons = el.querySelectorAll('[data-set-state]');
    for (const state_change_button of state_change_buttons) {
        state_change_button.addEventListener('click', function() {
            el.setAttribute("data-state", this.getAttribute("data-set-state"));
        });
    }
}

function main() {
    const stateful_elements = document.querySelectorAll("[data-state]")

    for (const el of stateful_elements) {
        makeStateful(el);
    }
}

main();
