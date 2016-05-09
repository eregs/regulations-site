def scroll_to(driver, selector, offset=20):
    cmd = 'window.scroll(0, $("{selector}").offset().top + {offset})'.format(
        selector=selector, offset=offset)
    driver.execute_script(cmd)
