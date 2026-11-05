# 電子書籍のビルド（pandoc が必要）
CHAPTERS := $(sort $(wildcard manuscript/*.md))
OUT      := dist/monozukuri-kimo.epub
COVER    := $(wildcard cover.jpg)

.PHONY: epub count clean
epub: $(OUT)

$(OUT): metadata.yaml $(CHAPTERS) style.css
	mkdir -p dist
	pandoc metadata.yaml $(CHAPTERS) \
	  --toc --toc-depth=1 --split-level=1 \
	  --css=style.css \
	  $(if $(COVER),--epub-cover-image=$(COVER)) \
	  -o $@

count:
	@for f in $(CHAPTERS); do printf '%6d  %s\n' $$(LC_ALL=C.UTF-8 wc -m < $$f) $$f; done
	@printf '%6d  合計\n' $$(cat $(CHAPTERS) | LC_ALL=C.UTF-8 wc -m)

clean:
	rm -f $(OUT)
