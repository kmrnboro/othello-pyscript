class MockElement:
    def __init__(self, *args, **kwargs):
        self.value = "none"
        self.checked = False
        self.innerText = ""
        self.innerHTML = ""
        self.classList = MockClassList()
        self.dataset = MockDataset()
        self.childElementCount = 0

    def getElementById(self, id):
        return MockElement()
    
    def querySelectorAll(self, selector):
        return []

    def createElement(self, tag):
        return MockElement()

    def appendChild(self, child):
        pass

class MockClassList:
    def add(self, *args): pass
    def remove(self, *args): pass

class MockDataset:
    def __init__(self):
        self.row = "0"
        self.col = "0"

document = MockElement()
window = MockElement()
