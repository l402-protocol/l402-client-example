# L402 Client Examples

This repository contains example implementations of L402 protocol clients using various frameworks and the following payment methods:

- [Lightspark](https://www.lightspark.com/)
- [Coinbase](https://commerce.coinbase.com/) (coming soon)
- [Stripe](https://stripe.com/) (coming soon)

## Prerequisites

### Lightspark

- A Lightspark account
- Environment variables (see `.env.example` in each example directory)

## Examples

### Python

Demos showcase how to integrate the L402 protocol for pay-per-request API access using a stock price API. 

Each example retrieves the financial information of one or more stocks and uses an LLM to analyze the data with the following frameworks:

- **OpenAI**: 
- **LangChain**: 
- **CrewAI**: 

You can test the API using a UI at [stock.l402.org](https://stock.l402.org/).

Initially you get 1 free credit to try it out. Subsequent requests will return a `402 Payment Required` error with a list of payment offers in JSON:

```json
{
    "expiry": "2024-12-03T14:12:53+00:00",
    "offers": [
        {
            "amount": 1,
            "currency": "USD",
            "description": "Purchase 1 credit for API access",
            "id": "offer_c668e0c0",
            "payment_methods": [
                {
                    "payment_details": {
                        "payment_request": "lnbc100n1pn57zd3pp5sfahhn6zha3s7ej3hjwzxjtyqsmjm7ahu7aq2m997gcjg4t0c6fqdq6xysyxun9v35hggzsv93kkct8v5cqzpgxqrzpnrzjqwghf7zxvfkxq5a6sr65g0gdkv768p83mhsnt0msszapamzx2qvuxqqqqz99gpz55yqqqqqqqqqqqqqq9qrzjq25carzepgd4vqsyn44jrk85ezrpju92xyrk9apw4cdjh6yrwt5jgqqqqz99gpz55yqqqqqqqqqqqqqq9qsp59new9m0ydspjf5rurvx62jutha2u7ezqkkjqwuzxnkl0cg20e93s9qxpqysgqulyvj8lu0frd5cr9twhd795lx6ktytwpnheyn6xyul69e7n0g895s4uefnczck2h2lk6y5lr5hqu6acravkam9zkatrk6x77ajdv78sq3sytx9"
                    },
                    "payment_type": "lightning"
                }
            ],
            "title": "1 Credit Package"
        },
        {
            "amount": 100,
            "currency": "USD",
            "description": "Purchase 120 credits for API access",
            "id": "offer_97bf23f7",
            "payment_methods": [
                {
                    "payment_details": {
                        "contract_addresses": {
                            "1": "0x1FA57f879417e029Ef57D7Ce915b0aA56A507C31",
                            "137": "0x288844216a63638381784E0C1081A3826fD5a2E4",
                            "8453": "0x03059433BCdB6144624cC2443159D9445C32b7a8"
                        },
                        "payment_request": "https://commerce.coinbase.com/pay/a771a693-d0a5-43bc-8f42-e72b1e245479"
                    },
                    "payment_type": "coinbase"
                },
                {
                    "payment_details": {
                        "payment_request": "lnbc10560n1pn57zd3pp5mvgs8texgczacay2l9h2az5nl5wwu5vw98f4djsu4hfyyk8p9jcsdqlxyerqgzrwfjkg6t5wvs9qctrddskwegcqzpgxqrzpnrzjqwghf7zxvfkxq5a6sr65g0gdkv768p83mhsnt0msszapamzx2qvuxqqqqz99gpz55yqqqqqqqqqqqqqq9qrzjq25carzepgd4vqsyn44jrk85ezrpju92xyrk9apw4cdjh6yrwt5jgqqqqz99gpz55yqqqqqqqqqqqqqq9qsp57jeykgmwajl5ytudzezgxhz8hg5eklayd2syvw8rudjd7turs3ws9qxpqysgq50ng2nrjgg9jh44v232l62h85xq9n5sr5ykucetytqfwpn5qmxmjg8u4e0f7eggwuteq4rjv9gj3nf3tekv3ak3w95w543apwkcmm4cqcy3mqd"
                    },
                    "payment_type": "lightning"
                }
            ],
            "title": "120 Credits Package"
        },
        {
            "amount": 499,
            "currency": "USD",
            "description": "Purchase 750 credits for API access",
            "id": "offer_a896b13c",
            "payment_methods": [
                {
                    "payment_details": {
                        "contract_addresses": {
                            "1": "0x1FA57f879417e029Ef57D7Ce915b0aA56A507C31",
                            "137": "0x288844216a63638381784E0C1081A3826fD5a2E4",
                            "8453": "0x03059433BCdB6144624cC2443159D9445C32b7a8"
                        },
                        "payment_request": "https://commerce.coinbase.com/pay/a2af323e-51f1-4ef6-b7c7-5a9221d898fd"
                    },
                    "payment_type": "coinbase"
                },
                {
                    "payment_details": {
                        "payment_request": "lnbc52740n1pn57zdjpp59t7a7u08guyjj0gu66z6t89hylsqx6f46vlvekxp0yfgx39d3e8sdqlxu6nqgzrwfjkg6t5wvs9qctrddskwegcqzpgxqrzpjrzjqwghf7zxvfkxq5a6sr65g0gdkv768p83mhsnt0msszapamzx2qvuxqqqqz99gpz55yqqqqqqqqqqqqqq9qrzjq25carzepgd4vqsyn44jrk85ezrpju92xyrk9apw4cdjh6yrwt5jgqqqqz99gpz55yqqqqqqqqqqqqqq9qsp5w2x05yd9u3yq8p33umkqhnmuc7al767y2lspjmu2gtua05nu586s9qxpqysgq76fqetphyf0ycttrsryz0qtc235y9aud69x9emdsqudt34jdh6vs67ws8mu4mmr6c4kgdzs2nlfu3q33w2and9u9mk94j44p9k2c4kcq8ka5zt"
                    },
                    "payment_type": "lightning"
                },
                {
                    "payment_details": {
                        "payment_link": "https://checkout.stripe.com/c/pay/cs_test_a1JmVRedcPDSecNy9s4lB6N2BPcJWgBKWeAT1EcKcXFvXYyR9KbtBnKcSX#fidkdWxOYHwnPyd1blpxYHZxWjA0S3VzXDdBbTFNVlJzfDVRT2pxd3AyandqTmAzSEdMYDZUa05yY1VKNWZOUXNVc09ITUdjUGNUUjB2TTVtUkBmVGxmSD1qN0JpZkBuTlMxNm1LcVFtdDVQNTVEc21jdWtoTCcpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"
                    },
                    "payment_type": "stripe"
                }
            ],
            "title": "750 Credits Package"
        }
    ],
    "terms_url": "https://link-to-terms.com",
    "version": "0.1"
}
```

Each example directory contains its own README with specific setup instructions and usage details.

## Getting Started

1. Clone the repository
2. Choose an example from the `python/examples` directory
3. Follow the README instructions in the chosen example directory

## License

MIT License - see LICENSE file for details