{% if travis_ci %}[![Build Status]({{ travis_ci.url }}.png?branch={{ travis_ci.branch }})](travis_ci.url){% endif %}

**Author:** {{ full_name }}. {% if twitter %}[Follow me on Twitter](twitter){% endif %}


## Installation

Install using `pip`...

    pip install {{ appname }}

...or clone the project from github.

    git clone https://github.com/{{ github_username }}/{{ appname }}.git


## Documentation
[docs]


{% if twitter %}[twitter]: https://twitter.com/{{ twitter }}{% endif %}
[docs]: https://github.com/{{ github_username }}/{{ appname }}
