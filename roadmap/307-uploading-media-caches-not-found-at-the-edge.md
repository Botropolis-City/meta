# 307. Uploading the site's media caches "not found" at the edge for clips about to exist

**Open. Filed 2026-10-27 (r1192), from 0.3.3's website release. Nobody's call — a defect.**

Publishing 0.3.3's re-film, `tools/upload-media.sh` checked whether each clip already existed with a request through `media.botropolis.city`, and the site's tests asked for them too, before the upload; Cloudflare's edge cached the 404s for four hours, so 28 of 30 new clips read as missing there after they were uploaded.
The manager purged the host's cache through the API, once Aria gave the deploy token *Zone → Cache Purge* on 2026-10-27.

## The fix

1. Check what exists in the bucket itself (R2's API, through the token), never through the cached host.
2. After an upload, purge the uploaded URLs (or the host) through Cloudflare's API with the deploy token, by reference through `secret-run`, never on a command line.
3. Tests: the existence check never requests the public host; an upload ends with a purge of exactly what it uploaded; a purge that fails fails the upload, saying why.
