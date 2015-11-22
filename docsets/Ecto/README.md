Ecto
=======================

#### Author:

Hideshi Ogoshi (https://github.com/hideshi)


#### How to generate the docset

- Clone Ecto project
`
git clone https://github.com/elixir-lang/ecto.git
`

- Checkout specific version
`
cd ecto
git checkout v1.0.6
`

- Add dependency in deps in mix.exs
`
{:ex_doc_dash, "~> 0.0", only: :docs}
`

- Fetch dependency
`
MIX_ENV=docs mix deps.get
`

- Generate docset
`
MIX_ENV=docs mix docs.dash
`

- Generated docset will be in doc directory
