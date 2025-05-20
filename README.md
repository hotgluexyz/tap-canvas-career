# tap-canvas-career

`tap-canvas-career` is a Singer tap for the Instructure [Canvas LMS API](https://canvas.instructure.com/doc/api/index.html).

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

You can install this tap directly from the GitHub repository using pipx:

```bash
pipx install git+https://github.com/your-org-or-username/tap-canvas-career.git
```

## Configuration

### Accepted Config Options

Create a config file containing the Canvas API credentials, e.g.:

```json
{
  "base_url": "xxxx.cd.instructure.com",
  "account_id": "self",
  "client_id": "xxxxxxxxxxxxxxxxxxxxxxxx",
  "client_secret": "xxxxxxxxxxxxxxxx",
  "refresh_token": "xxxxxxxxxxxxxxxxxxxxxxxx",
  "start_date": "2017-01-01T00:00:00Z",
}
```

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-canvas-career --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `tap-canvas-career` by itself or in a pipeline like [hotglue](https://hotglue.com/).

### Executing the Tap Directly

```bash
tap-canvas-career --version
tap-canvas-career --help
tap-canvas-career --config CONFIG --discover > ./catalog.json
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
