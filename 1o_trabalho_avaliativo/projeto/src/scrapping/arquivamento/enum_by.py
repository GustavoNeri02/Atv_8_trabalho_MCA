# for enum class, example:
from enum import Enum
from selenium.webdriver.common.by import By

EnumBy = Enum('EnumBy', [('xpath', By.XPATH), ('link', By.LINK_TEXT), ('id', By.ID), ('name', By.NAME)])