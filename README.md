# Trademan

Asynchronous Python trading helper for Tinkoff clients with a Django backend. A pet-project started while learning Python @ Yandex.Practicum to improve programming skills, learn asynchronous programming and help me to:
- Buy or sell stocks / futures at better prices without hassle
- Improve MOEX functionality available at Tinkoff Investments, making it possible to create market delta-neutral positions: calendar spreads featuring a future as a far leg and future or stock as a near leg. Capture better prices.
- Automate routine tasks like placing alot of stop-like orders to buy stocks when the market crashes or cancel many orders at maximum speed.

This product is provided as is, it's a educational product, use it at your own risk and be sure to check the working logic, as it works with real assets on your broker account. 

I use it on a Raspberry Pi, which adds some complications to find a working combination of OS image and Python version that works with all dependencies on ARMv7 architecture, bear with it - some instructions in Dockerfiles might seem too complicated and excessive, but it's working this way and it's easier to run/stop a container stack via Portainer web-interface then to run virtual environments for both front- and backend.

This is already 3rd iteration of the product and it's under heavy development - I'm learning through constant refactoring, it's a pretty painful, but working strategy.

Despite the fact that this is an English-language portfolio, the product itself will not be translated to English, because you have to speak Russian in order to use Tinkoff Broker.