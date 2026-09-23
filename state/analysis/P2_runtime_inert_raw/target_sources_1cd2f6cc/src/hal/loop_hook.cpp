// Overrides the inherited weak Bridge hook without importing its definition.
// Keeps application loop completion free of the stock blocking Bridge update.
// Actual target symbol, body and main relocation inspection test this override.
void __loopHook() {}
