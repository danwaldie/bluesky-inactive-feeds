from . import inactive

algos = {
    'at://did:plc:YOUR_DID/app.bsky.feed.generator/inactive-7d': inactive.get_handler(7),
    'at://did:plc:YOUR_DID/app.bsky.feed.generator/inactive-30d': inactive.get_handler(30),
    'at://did:plc:YOUR_DID/app.bsky.feed.generator/inactive-120d': inactive.get_handler(120),
}
