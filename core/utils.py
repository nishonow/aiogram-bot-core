from aiogram.types import ChatMemberStatus
from core.db import get_channel_ids
from loader import bot

from aiogram.types import ChatMemberStatus


async def check_channel_membership(user_id: int) -> bool:
    required_channels = get_channel_ids()  # Fetch channel IDs from the database

    if not required_channels:
        # No channels in the database, consider the user as subscribed
        return True

    for channel_id in required_channels:
        try:
            chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            # Check if the user is a member or has a valid status (admin/owner)
            if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR,
                                          ChatMemberStatus.OWNER]:
                return False
        except Exception:  # Handle invalid channel or bot not being an admin in the channel
            return False

    return True


FUN_FACTS = [
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
    "Octopuses have three hearts, and two of them stop beating when they swim.",
    "Bananas are berries, but strawberries are not!",
    "The Eiffel Tower can grow more than 6 inches during summer due to thermal expansion.",
    "A group of flamingos is called a 'flamboyance'.",
    "Sloths can hold their breath longer than dolphins—up to 40 minutes!",
    "Sharks existed before trees—they've been around for over 400 million years.",
    "Wombat poop is cube-shaped, which helps it stay in place and mark their territory.",
    "The heart of a blue whale is so big that a human could swim through its arteries.",
    "There are more stars in the universe than grains of sand on Earth.",
    "The inventor of the Pringles can is buried in one—his ashes were placed inside a Pringles can.",
    "A day on Venus is longer than a year on Venus due to its slow rotation.",
    "Pineapples take about two years to grow before they're ready to harvest.",
    "Sea otters hold hands when they sleep to keep from drifting apart.",
    "The dot over the lowercase letters 'i' and 'j' is called a 'tittle'.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
    "Cows have best friends and get stressed when they are separated.",
    "An ostrich's eye is bigger than its brain.",
    "The first oranges weren’t orange—they were green.",
    "Koalas have fingerprints that are so similar to humans' that they can confuse crime scene investigators.",
    "Butterflies can taste with their feet.",
    "There’s a species of jellyfish that is biologically immortal. It can revert to its juvenile form indefinitely.",
    "A group of crows is called a 'murder'.",
    "A chef’s hat traditionally has 100 pleats to represent the 100 ways to cook an egg.",
    "The fingerprints of a koala are so indistinguishable from humans that they have been confused at crime scenes."
]
