# hx-complete

This extension provides Visual Studio Code with auto-completion support for [HTMX][htmx-main-page]'s v2 HTML attributes. It accomplishes this by contributing [custom data][vscode-custom-data] to VS Code's [HTML language service][vscode-html-languageservice].

Because this extension contributes to only this language service, it does not provide support for programming language or templating language file types. For example, VS Code will not understand that your `.js`, `.cshtml`, and `.jinja` files may contain HTMX attributes just because you installed this extension.

## Why this extension?

### v2 attribute support

This extension supports HTMX v2 while some of the other available extensions support HTMX v1.

I don't think there's anything wrong with that, especially because according to the project homepage:

> ... It is not currently marked as [`latest`](https://docs.npmjs.com/cli/v10/commands/npm-dist-tag#purpose) in NPM so that people using the [1.x line](https://v1.htmx.org/) are not accidentally upgraded.

### `data-*` attribute support

Unlike other extensions, this one also includes `data-*` attribute support.

While not highlighted throughout the [official documentation][htmx-docs], HTMX allows you to use `data-hx-*` attributes as an alternative to `hx-*` attributes for the sake of using standard HTML attributes. The feature is mentioned under the "htmx in a Nutshell" section of those docs.

> It's worth mentioning that, if you prefer, you can use the [`data-`](https://html.spec.whatwg.org/multipage/dom.html#attr-data-*) prefix when using htmx:
>
> ```html
> <a data-hx-post="/click">Click Me!</a>
> ```

## Should *you* install this extension?

### Probably if:

- You want HTMX v2 auto-completion support.
- You want that support to include `data-*` attributes.

### Probably not if: 

- You are using HTMX v1.
- You need incredibly detailed hover-over documentation.
- You need auto-completion in something other than `.html` files.

## Usage

This extension is available on:

- [Visual Studio Marketplace][visual-studio-marketplace]
- [Open VSX Registry][open-vsx-registry]
- [GitHub][github]

Choose the installation method you're comfortable with, and start writing HTML with HTMX.

## Screenshots

![auto-completion example][example-gif]

## License

This extension is licensed under the very permissive, open-source BSD-3 Clause license. Details can be found in [`LICENSE.md`](./LICENSE.md).

The TL;DR of the license is that you can do whatever you want with the extension so long as you don't claim I endorse it.


[example-gif]: https://github.com/pfeif/hx-complete/blob/main/static/example.gif?raw=true
[github]: https://github.com/pfeif/hx-complete
[htmx-docs]: https://htmx.org/docs/
[htmx-main-page]: https://htmx.org/
[open-vsx-registry]: https://open-vsx.org/extension/pfeif/hx-complete
[visual-studio-marketplace]: https://marketplace.visualstudio.com/items?itemName=pfeif.hx-complete
[vscode-custom-data]: https://github.com/microsoft/vscode-custom-data
[vscode-html-languageservice]: https://github.com/microsoft/vscode-html-languageservice