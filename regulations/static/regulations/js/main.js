import RelatedRules from './RelatedRules.js';
import Vue from "../../node_modules/vue/dist/vue.esm.browser.min.js";

function isElementInViewport (el) {
    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
    );
}

function deactivateAllTOCLinks() {
    const active_els = document.querySelectorAll(".menu-section.active");
    for (let active_el of active_els) {
        active_el.classList.remove("active");
    }
}

function getCurrentSectionFromHash() {
    const hash = window.location.hash.substring(1);
    const citations = hash.split("-");
    return citations.slice(0, 2).join("-");
}

function activateTOCLink() {
    deactivateAllTOCLinks();
    const section = getCurrentSectionFromHash();

    const el = document.querySelector(`[data-section-id='${section}']`);
    if (!el) return;

    el.classList.add("active");
    if (!isElementInViewport(el)) {
        el.scrollIntoView();
    }
}

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

function main() {
    const stateful_elements = document.querySelectorAll("[data-state]")

    for (const el of stateful_elements) {
        makeStateful(el);
    }

    window.addEventListener("hashchange", activateTOCLink);
    activateTOCLink();

    
    new Vue({
        components: {
            RelatedRules,
        }
    }).$mount("#related-rules")
}

main();
