#import "XiblessSupport.h"

@implementation XiblessToolbarDelegate
- (id)init
{
    self = [super init];
    items = [[NSMutableDictionary alloc] init];
    defaultItems = nil;
    return self;
}

- (void)dealloc
{
    [items release];
    [defaultItems release];
    [super dealloc];
}

- (void)addItem:(NSToolbarItem *)aItem
{
    [items setObject:aItem forKey:[aItem itemIdentifier]];
}

- (void)setDefaultItems:(NSArray *)aDefaultItems
{
    [defaultItems release];
    defaultItems = [aDefaultItems retain];
}

- (NSToolbarItem *)toolbar:(NSToolbar *)toolbar itemForItemIdentifier:(NSString *)itemIdentifier willBeInsertedIntoToolbar:(BOOL)flag
{
    return [items objectForKey:itemIdentifier];
}

- (NSArray *)toolbarAllowedItemIdentifiers:(NSToolbar *)toolbar
{
    NSMutableArray *result = [NSMutableArray array];
    [result addObject:NSToolbarSeparatorItemIdentifier];
    [result addObject:NSToolbarSpaceItemIdentifier];
    [result addObject:NSToolbarFlexibleSpaceItemIdentifier];
    [result addObjectsFromArray:[items allKeys]];
    return result;
}

- (NSArray *)toolbarDefaultItemIdentifiers:(NSToolbar *)toolbar
{
    return defaultItems;
}
@end

NSString* stringFromChar(unichar c)
{
    return [NSString stringWithCharacters:&c length:1];
}

void setAccessibilityDescription(id obj, NSString *description)
{
    id accessibilityObject = NSAccessibilityUnignoredDescendant(obj);
    [accessibilityObject accessibilitySetOverrideValue:description forAttribute:NSAccessibilityDescriptionAttribute];
}

void setAccessibilityDescriptionOfChild(id obj, NSInteger childIndex, NSString *description)
{
    id accessibilityObject = NSAccessibilityUnignoredDescendant(obj);
    NSArray *children = [accessibilityObject accessibilityAttributeValue:NSAccessibilityChildrenAttribute];
    
    if (childIndex >= [children count]) {
        NSLog(@"childIndex out of bounds in setAccessibilityDescriptionOfChild");
        return;
    }
    
    id child = [children objectAtIndex:childIndex];
    [child accessibilitySetOverrideValue:description forAttribute:NSAccessibilityDescriptionAttribute];
}
