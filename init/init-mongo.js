

db = db.getSiblingDB("llm");


// Create collections
db.createCollection("Prompt");
db.createCollection("Conversation");
db.createCollection("ConversationFull");
db.createCollection("ConversationPOST");
db.createCollection("ConversationPUT");

