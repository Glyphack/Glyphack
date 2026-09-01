---
date: 2026-08-19
category:
  - "Blog"
tags:
  - Active
title: Running Python Tests in Ty
---
The last thing I worked on in [Ty](https://docs.astral.sh/ty/) was adding [Pytest support](https://github.com/astral-sh/ty/issues/1986).
Pytest integration is a broad topic; more specifically, I wanted to build a test runner, so you can run tests from the editor.

This post is based on the code in my [PR](https://github.com/astral-sh/ruff/pull/24512).
Although this is not merged in Ty, I'm going to talk about what are the ways to add a test runner to a language server in this post.

Before that, let's see a quick demo of what it looks like.

Showing individual tests in a file:

![ty-codelens-run-test.mp4](ty-codelens-run-test.mp4)

Test Explorer (the UI is done with [neotest](https://github.com/nvim-neotest/neotest)):

![ty-test-explorer-neovim.mp4](ty-test-explorer-neovim.mp4)

The reason I'm interested in running tests is that I usually want to try something in the code, without having to run it from the application.
Writing a test is a way to achieve this. I write a test, call the function that I want to check, and see what it does. Right where it is.
Being able to trigger that test from the editor means that I don't need to open a terminal window.
I also like to have the option to edit a test and run it during debugging.
I can do this with [watchexec](https://github.com/watchexec/watchexec), but if I can trigger from the editor, I don't have to copy the test name.

Language servers take different approaches to showing and running tests, because LSP does not provide support for test runner integration.

The usual approaches are:

1. The editor has the logic to detect tests, either from names (Go tests are easy to detect because of how they look) or using external tools.
    The Python VS Code extension runs a `pytest --collect-only` to collect the tests and show it.
    This has the drawback that one syntax error fails the whole test discovery.
2. The server exposes the tests and the client makes a request.
    There are two paths here: either use [Code Lens](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_codeLens)[^1] which is standard and works in every editor(and accept the poor experience) or [define custom](https://shopify.github.io/ruby-lsp/test_explorer.html#other-editors)[^2] LSP requests for better experience.
3. Use code actions. Editor does not show a hint for the test and the option for running the test shows up in a menu along with other actions like "Sort Imports".
    I only know Go uses it. But I have never enabled it.

---

I started implementing this using code lens and in the server. I _think_ Code Lens works in every editor with LSP support.
I checked Neovim only.

Code lens is a way for the server to let the editor know that something special is available at this line.
It shows a visual hint, so you can show "Run Test" above the test and can carry a command.
This is not specific to tests and any useful text with an action can be shown there.

The response after client requests code lenses for a file looks like this:

```
CodeLens {
	range: Range;
	command?: Command;
	data?: LSPAny;
}
```

Range tells the client where the hint should be shown.
Command carries what action is available:

```
{
"title": "Run Test"
"command": "ty.runTest"
"arguments": {"cwd": "project_root", "program": "./venv/bin/python", "arguments": ["-m", "pytest", "sample_test"]}
}
```

This tells the client to run the `runTest` command when the user triggers this code lens action.
`runTest` is not an editor or terminal command. It's custom command defined by the server.
Whoever handles it uses the `arguments` field to figure out what's the actual command to run.
Server chooses what Python interpreter to use (huge problem in Python world!) and what's the working directory of the project, which makes the client implementation simpler.

Triggering code lens sends an [execute command request](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#executeCommandParams) to the server.
Server can execute this command in another thread to separate it from other language server work.
After the command finishes the server can either return the response or notify the client via `showMessage`.
I chose `showMessage` because the returned response has no standard handle path.

```rust
std::thread::spawn(move || {
    match std::process::Command::new(&run_test_args.program)
        .args(&run_test_args.arguments)
        .current_dir(std::path::PathBuf::from(&run_test_args.cwd))
        .output()
    {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);

            if output.status.success() {
                client.show_message(
                    format!("passed\n{stdout}\n command: {run_test_args}"),
                    types::MessageType::INFO,
                );
            } else {
                client.show_message(
                    format!("\nfailed\n{stdout}\n{stderr}\n command: {run_test_args}"),
                    types::MessageType::ERROR,
                );
            }
        }
        ...
    }
});
```

I ran this and it worked! But I wanted better.
Specifically, show the output in a window that I can scroll and search, preferably a terminal window.

In this way the test output [shows up](https://github.com/golang/go/issues/67400) in a notification window:

> Each client displays the streamed output and final showMessage in a different UI element: VS Code feeds it into a sticky dialog box; Vim accumulates the stream into a buffer which is displayed at the end. Emacs+eglot displays the output in the little echo area (bottom line), which is ephemeral and not suitable for large amounts of text.

Is defining custom LSP methods the only way to have nicer outputs? This would be pretty sad.
But you know this post is not finished so you know there must be another way!

During my experiments I realized that the VS Code extension can also register commands.
Commands are executed on the client if it's defined otherwise it would send a request to the server with command and arguments.
This mechanism is also implemented in other LSP servers. Note that I just tested VS Code and Neovim, this might not be universal.

The user is in one of these three situations:

- He uses an editor with LSP support with no custom config. The client sends this command to the server, and the server runs the test using `arguments`.
- He uses VS Code, the extension has a custom code that intercepts command running and handles running the test using Tasks API and shows the output in a new pane.
- He uses an editor with LSP support he can customize the test running behavior of Ty with a bit of code.

The second and third point can be implemented like this:

```lua
vim.api.nvim_create_autocmd("LspAttach", {
group = vim.api.nvim_create_augroup("lsp-attach", { clear = true }),
callback = function(event)
    local client = vim.lsp.get_client_by_id(event.data.client_id)
    if client == nil then
        return
    end
    if client.name == "ty" then
        vim.lsp.commands["ty.runTest"] = function(command)
            local run_test = command.arguments and command.arguments[1]
            if run_test == nil then
                vim.notify("Failed to run test: server sent incomplete arguments", vim.log.levels.ERROR)
                return
            end
            local cwd = run_test.cwd
            local program = run_test.program
            local cmd_args = run_test.arguments
            local cmd_str = program .. " " .. table.concat(cmd_args, " ")
            vim.cmd("split | terminal cd " .. vim.fn.shellescape(cwd) .. " && " .. cmd_str)
        end
    end
end,
})
```
Most of this code is just boilerplate.
The important piece is to define a custom handler for `ty.runTest` that runs the test in a terminal.

This is essentially what the VS Code extension also contains:

```js
/**
 * Creates a test runner for the `ty.RunTest` command.
 * This will run the test in a new terminal.
 */
export function createRunTestProvider() {
  return async (runTest: RunTestArgs | undefined) => {
    if (runTest == null) {
      logger.error("Failed to run test: missing 'RunTest' arguments");
      vscode.window
        .showErrorMessage("Failed to run test: missing required arguments.", "Show Logs")
        .then((selection) => {
          if (selection) {
            logger.channel.show();
          }
        });
      return;
    }

    const { cwd, program, arguments: programArgs, testTarget } = runTest;
    const task = new vscode.Task(
      { type: "shell" },
      vscode.TaskScope.Workspace,
      `${testTarget}`,
      `ty`,
      new vscode.ShellExecution(program, programArgs, { cwd }),
    );
    task.presentationOptions = {
      reveal: vscode.TaskRevealKind.Always,
      panel: vscode.TaskPanelKind.Dedicated,
      clear: true,
    };
    const execution = await vscode.tasks.executeTask(task);
    await new Promise<void>((resolve) => {
      const listener = vscode.tasks.onDidEndTaskProcess((e) => {
        if (e.execution === execution) {
          listener.dispose();
          if (e.exitCode !== 0) {
            logger.error(`Running test failed: ${program} ${programArgs.join(" ")}`);
          }
          resolve();
        }
      });
    });
  };
}
```

---

After I sent this for review the maintainer made some [suggestions](https://github.com/astral-sh/ruff/pull/24512#issuecomment-5034134928).
The summary was:
- Don't run tests on the server because of limitations like you cannot tell the server to stop the test
- It's nice to also have [test explorer](https://code.visualstudio.com/docs/debugtest/testing#_automatic-test-discovery-in-testing-view) functionality. Although I never used test explorer functionality regularly I was open to trying it.
    I can now say it's quite nice to have a watch mode that runs a test on each edit!

The first part can be done without changing the communication format.
Just remove the server side execution of the command and show the code lens if the client supports running the tests.
But to provide test explorer functionality I had to define a custom LSP request.
Because there's no such thing in LSP(unless your imagination can misuse another feature).

I adopted the approach Rust analyzer does.
Rust analyzer uses exclusive requests for [fetching and running](https://rust-analyzer.github.io/book/contributing/lsp-extensions.html#test-explorer) tests.
The drawback is that it [requires a plugin](https://github.com/neovim/neovim/issues/14874) to work.

I made one modification to this design.
Rust analyzer uses push notifications to notify test changes to the client.
I decided to rely on client asking for tests whenever a file changes, instead of implementing the notification to tell the client what changed in tests.
A newer version of the client with push mechanism can have a flag to change this. Server can send notifications if client supports it.

This is how it works:

1. Upon start client sends a `ty/discoverTests` to get all project tests.
2. Client adds a listener on events, `onDidChange`, `onDidDelete`, etc. and request the tests again via the same endpoint when something changes.
3. To run it, client sends the test id to `ty/resolveRunTestParams` and gets back the working directory and the command to execute.


A second request for getting the command to run adds a round trip to the server, which sounds unnecessary because the server could just return the command.
But it's useful for the future if client wants to execute in different ways like debugging or running it.

This is the body of `ty/discoverTests` request:
```typescript
interface discoverTestsParams {
    uri?: URI;
}
```

If the URI is null the server would return all the tests. Otherwise, it limits the tests to asked file/directory.

The response can be defined as:

```typescript
interface TestItem {
    // Pytest node id for this item
    id: String,
    // The kind of this item. Directory, or File, or Class, or Function.
    kind: TestItemKind,
    // The display name of this item, e.g. `test_bar`.
    label: String,
    // The id of the parent of this item, or `None` if it is a top-level item.
    parent?: String,
    // The range of this item's name in its file, if it has one (directories and files don't).
    range?: Range,
    // uri of the test item
    uri?: URI,
}
```

The tests are rendered as a tree in the editor so navigating them is easier. The `parent` field determines this tree structure.
This response contains the complete list of tests from the child to the root of tests.
So if you have a test named `test_example` in `tests/my_test.py` then the tests returned are:

```[test_example, tests/my_test.py, tests]```

When a test needs to be executed, the client sends a `ty/resolveRunTestParams` request.
The `test_id` is Pytest [node identifier](https://docs.pytest.org/en/stable/example/markers.html#node-id).
This is a string like `tests/my_test.py::tests`.
Node identifier is all the server needs to generate a command that runs the test so the client can run it.

```typescript
interface ResolveRunTestParamsParams {
    test_id: string;
}
```

To which the server responds with the same arguments that the code lens command had:

```typescript
interface RunTestParams {
    working_directory: string;
    program: string;
    arguments: string[];
}
```

---

Every time I think of some feature that I want from the language server but it's not there I find some issue that is a few years old.
It was the same story here again.
Every language server implementer has to implement something slightly differently because there is no standard.

It's slow and hard to define the behavior of software.
Even this PR is taking longer to finish than my other work because whatever is provided will be used by users and has to be supported.
Which is the same idea with LSP.
Adding new features to the protocol is slow.

I think the test running should happen on the client side actually.
But it needs its dedicated command type so the client knows how to handle that command.
It can also be extended to commands other than test.

This might be something that [debug adapter protocol](https://microsoft.github.io/debug-adapter-protocol/overview.html) can already do and we need to bridge a gap from commands to it?

Currently I'm waiting for another blocking comment on the PR.
Another maintainer is going to implement the test discovery(finding where the tests are) into a separate PR so then I remove section of the code from my PR.
I skipped this topic entirely because I don't think there's anything interesting there.

---

[^1]: I found the Go test runner logic both in [server](https://github.com/golang/tools/blob/746b959debf8e54650c0a69332595941289d1a62/gopls/internal/golang/code_lens.go#L37) and [client](https://github.com/golang/vscode-go/blob/46048018519b6f727e920f5f5a4335acc436bdd3/extension/src/goTest.ts#L420).
	This means that Gopls will tell the editor where code lenses are.
	If your editor is VS code then the go extension will handle running this test so you get a nice terminal window running that test.
	But if you run this in Neovim the server handles running the test.

	When server runs the test it sends back the output to the client as a notification.
	This cannot stream output for slow tests so for something that takes few seconds to finish is not a good UX.
	It's better to not have such tests but sometimes you have got to work with other people's code.
	There's an [issue](https://github.com/microsoft/language-server-protocol/issues/2014) on LSP for adding such option.
	So the approach they took works well with an extension like VS code and offers minimum functionality in other editors.

	This is what Alan uses as a fallback on Emacs:

	> Personally I use a custom Emacs Lisp function to fork+exec 'gopls codelens' through Emacs' compile package, so that its output is immediately streamed into a first-class editor buffer. I like this because it is immediate, real-time, editable, searchable, and durable, and because it displays the test logs even when the test passes, which is sometimes helpful. Also, Emacs treats the buffer just like a compiler output, so that locations become links, etc. The UX here is pretty close to ideal for me, but the mechanism is very clunky, and of course no-one but me benefits from it.

[^2]: Rust analyzer uses exclusive requests for [fetching and running](https://rust-analyzer.github.io/book/contributing/lsp-extensions.html#test-explorer) tests.
	This is not part of the LSP.
	So in order to overcome the challenges that Go faced they have better requests for handling running the test.
	The drawback is that it [requires a plugin](https://github.com/neovim/neovim/issues/14874) to work.
	To fetch the tests client sends a request to the server asking for the tests in the project.
	```typescript
	interface DiscoverTestParams {
		// The test that we need to resolve its children. If not present,
		// the response should return top level tests.
		testId?: string | undefined;
	}
	```
	Server responds back with a list of discovered tests. Just keeping what we care about right now, how to run the test.
	```typescript
	interface TestItem {
		// A unique identifier for the test
		id: string;
		...
		// The information useful for running the test. The client can use `runTest`
		// request for simple execution, but for more complex execution forms
		// like debugging, this field is useful.
		// Note that this field includes some information about label and location as well, but
		// those exist just for keeping things in sync with other methods of running runnables
		// (for example using one consistent name in the vscode's launch.json) so for any purpose
		// other than running tests this field should not be used.
		runnable?: Runnable | undefined;
	};
	```
	
	The [runnable](https://rust-analyzer.github.io/book/contributing/lsp-extensions.html#runnables) defines how to run this test.

	After the initial delivery of the tests the server notifies the client about changes that happened to tests so the client can update the its state.
	This was not an issue for codelens because editors already re-request code lenses on updates.
	But for a custom request you need a way to update the old test information.
	This is done by sending a notification to the client every time a test changes. It tells the client tests in what scopes(files, modules) have to be replaced with the new tests given.
	This way the server does not have to say update `file1.test_name_1` to `file1.test_name_2` and does not need to keep track of what tests were sent to the client.
	Instead it just says: "replace all the tests in the given file with the tests in the response".
	
	```typescript
	interface DiscoverTestResults {
	    // The discovered tests.
	    tests: TestItem[];
	    // For each test whose id is in this list, the response
	    // contains all tests that are children of this test, and
	    // client should remove old tests not included in the response.
	    scope: string[] | undefined;
	    // For each file whose uri is in this list, the response
	    // contains all tests that are located in this file, and
	    // client should remove old tests not included in the response.
	    scopeFile: lc.TextDocumentIdentifier[] | undefined;
	}
	```
