# Profile artwork

These SVGs are custom artwork for the vinzify GitHub profile. Dark and light
variants share the same composition. Typography is outlined so the images do
not depend on a visitor's installed fonts or external font services.

The lettering uses IBM Plex Sans Condensed, IBM Plex Mono, and Lato, which are
available under the SIL Open Font License. The project interfaces in the artwork
are illustrations rather than screenshots or live statistics.

To regenerate the artwork on Linux, install the fonts and Fontconfig, then run:

```sh
uv run --with fonttools python assets/generate.py assets
```
