from selenium import common
import interface as i


def start():
    i.open_window("https://play.pokemonshowdown.com")
    i.log_in("cs232-test-1", "cs232")
    i.find_randbat()