from helpers import scraping
from helpers import converter
from helpers import helpers


class Substance:

    def __init__(self, name):
        self.name = name
        self.tag = helpers.name_to_tag(name)

        # Get the properties from NIST
        self.html_bs4 = self.get_html_bs4()
        self.molecular_weight = self.get_molecular_weight()
        self.antoine = self.get_antoine()

    def get_html_bs4(self):
        url = 'https://webbook.nist.gov/cgi/cbook.cgi?Name={0}&Mask=4'\
            .format(self.tag)
        return scraping.get_html_bs4(url)

    def get_molecular_weight(self):
        css_element = '#main > ul:nth-of-type(1) > li:nth-of-type(2)'
        li = scraping.scrap_properties(self.html_bs4, css_element).text
        return float(li.replace(" ", "").split(':')[1])

    def get_vapor_pressure(self, temperature):
        temperature = converter.temperature(temperature.value,
                                            temperature.units, 'k')
        for row in self.antoine:
            if row[0][0] <= temperature <= row[0][1]:
                A = row[1]
                B = row[2]
                C = row[3]
                return 10 ** (A - B/(C + temperature))

        return None    

    def get_antoine(self):
        css_element = 'table'
        unique_property = 'aria-label'
        property_value = 'Antoine Equation Parameters'
        table = scraping.scrap_properties(self.html_bs4, css_element,
                                          unique_property, property_value)

        # Extract the rows from the table. Knowing what tags have an HTML table.
        # Also, knowing that the fist row with he table header does not have the
        # class attribute 'exp' so we obtain just the rows with data.
        # The find_all function from BeautifulSoup return a list
        rows = table.find_all('tr', class_='exp')

        # Declaring the lists for storage Temperatures and coefficients.
        coefficients = []

        for row in rows:
            cols = row.find_all('td')
            A = float(cols[1].text)
            B = float(cols[2].text)
            C = float(cols[3].text)

            # For the temperatures, we have a range and we need to extract each
            # limit (lower and higher)
            lower_lim = float(cols[0].text.replace(" ", "").split('-')[0])
            higher_lim = float(cols[0].text.replace(" ", "").split('-')[1])
            temperatures = [lower_lim, higher_lim]

            coefficients.append([temperatures, A, B, C])

        return coefficients
