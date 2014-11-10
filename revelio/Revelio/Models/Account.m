//
//  Account.m
//  Revelio
//
//  Created by Christine Yen on 11/21/13.
//  Copyright (c) 2013 ChristineYen. All rights reserved.
//

#import "Account.h"
#import "Conversation.h"
#import "CYRAppDelegate.h"

@implementation Account

@dynamic handle;
@dynamic conversations;

- (BOOL)validateHandle:(id *)handleValue error:(NSError * __autoreleasing *)outError {
    NSFetchRequest *req = [NSFetchRequest fetchRequestWithEntityName:@"Account"];
    req.predicate = [NSPredicate predicateWithFormat:@"handle == %@", *handleValue];

    NSError *error = nil;
    CYRAppDelegate *appDelegate = (CYRAppDelegate *)[[NSApplication sharedApplication] delegate];
    NSInteger count = [appDelegate.managedObjectContext countForFetchRequest:req error:&error];
    if (error) {
        // TODO: remove, for debugging purposes
        NSLog(@"what? %@", error);
    }

    return count == 0 && !error;
}

@end